#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信群作业自动下载脚本
- 定时运行 (默认 15:00-20:00)
- 监听指定群聊，仅保存指定发布者的消息
- 自动按 日期/学科/文件类型 归类保存
- 支持: 文本、图片、视频、语音、文件、链接、笔记
"""

import os
import sys
import time
import yaml
import logging
import shutil
from pathlib import Path
from datetime import datetime, time as dt_time
from logging.handlers import RotatingFileHandler

try:
    from wxauto import WeChat
    from wxauto.msgs import *
except ImportError:
    print("请先安装依赖: pip install wxauto pyyaml apscheduler")
    sys.exit(1)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    print("请先安装依赖: pip install apscheduler")
    sys.exit(1)


class HomeworkBot:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.wx = None
        self.listened_chats = {}
        self.last_msg_hash = {}  # 去重用
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    def _load_config(self, path: str) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        # 展开环境变量
        config['save_root'] = os.path.expandvars(config['save_root'])
        return config

    def _setup_logging(self):
        log_cfg = self.config.get('logging', {})
        log_file = log_cfg.get('file', 'logs/homework_bot.log')
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        handlers = [
            RotatingFileHandler(
                log_file,
                maxBytes=log_cfg.get('max_bytes', 10485760),
                backupCount=log_cfg.get('backup_count', 5),
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
        
        logging.basicConfig(
            level=getattr(logging, log_cfg.get('level', 'INFO')),
            format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            handlers=handlers
        )

    def _is_in_schedule_window(self) -> bool:
        """检查当前时间是否在配置的时间窗口内"""
        now = datetime.now().time()
        start = dt_time(self.config['schedule']['start_hour'], self.config['schedule']['start_minute'])
        end = dt_time(self.config['schedule']['end_hour'], self.config['schedule']['end_minute'])
        return start <= now <= end

    def _init_wechat(self):
        """初始化微信客户端连接"""
        try:
            # 设置默认保存路径 (wxauto内部用)
            from wxauto import WxParam
            WxParam.DEFAULT_SAVE_PATH = self.config['save_root']
            
            self.wx = WeChat()
            self.logger.info("微信客户端连接成功")
            return True
        except Exception as e:
            self.logger.error(f"微信客户端连接失败: {e}")
            return False

    def _get_subject(self, group_name: str, content: str) -> str:
        """根据群配置的关键词判断学科"""
        group_cfg = next((g for g in self.config['groups'] if g['name'] == group_name), None)
        if not group_cfg:
            return "其他"
        
        content_lower = content.lower()
        for subject, keywords in group_cfg.get('subject_keywords', {}).items():
            for kw in keywords:
                if kw.lower() in content_lower:
                    return subject
        return "其他"

    def _get_type_dir(self, msg) -> str:
        """获取文件类型对应的目录名"""
        type_map = self.config.get('file_type_dirs', {})
        return type_map.get(msg.type, msg.type)

    def _build_save_path(self, group_name: str, subject: str, type_dir: str) -> Path:
        """构建保存路径: 根目录/群名/日期/学科/类型/"""
        today = datetime.now().strftime("%Y-%m-%d")
        safe_group = group_name.replace('/', '_').replace('\\', '_')
        path = Path(self.config['save_root']) / safe_group / today / subject / type_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _is_publisher(self, group_name: str, sender: str) -> bool:
        """判断发送者是否为配置的发布者"""
        group_cfg = next((g for g in self.config['groups'] if g['name'] == group_name), None)
        if not group_cfg:
            return False
        publishers = group_cfg.get('publishers', [])
        if not publishers:  # 空列表 = 不限制发送者
            return True
        return sender in publishers

    def _process_message(self, msg, group_name: str):
        """处理单条消息: 过滤、分类、下载保存"""
        # 1. 发送者过滤
        if not self._is_publisher(group_name, msg.sender):
            return
        
        # 2. 去重 (基于msg.hash)
        msg_key = f"{group_name}_{msg.hash}"
        if msg_key in self.last_msg_hash:
            return
        self.last_msg_hash[msg_key] = True
        
        # 3. 学科分类
        content = msg.content or ""
        subject = self._get_subject(group_name, content)
        type_dir = self._get_type_dir(msg)
        save_dir = self._build_save_path(group_name, subject, type_dir)
        
        # 4. 处理不同类型消息
        try:
            if msg.type == 'text':
                self._save_text(msg, save_dir, subject)
            elif msg.type == 'image':
                self._save_image(msg, save_dir)
            elif msg.type == 'video':
                self._save_video(msg, save_dir)
            elif msg.type == 'voice':
                self._save_voice(msg, save_dir)
            elif msg.type == 'file':
                self._save_file(msg, save_dir)
            elif msg.type == 'note':
                self._save_note(msg, save_dir)
            elif msg.type == 'link':
                self._save_link(msg, save_dir)
            else:
                self.logger.debug(f"未处理的消息类型: {msg.type} from {msg.sender}")
        except Exception as e:
            self.logger.error(f"保存消息失败 [{group_name}] {msg.sender}: {e}")

    def _save_text(self, msg, save_dir: Path, subject: str):
        """保存文本消息"""
        timestamp = datetime.fromtimestamp(msg.time).strftime("%H-%M-%S") if hasattr(msg, 'time') else datetime.now().strftime("%H-%M-%S")
        filename = f"{subject}_{msg.sender}_{timestamp}.txt"
        filepath = save_dir / filename
        content = f"发送者: {msg.sender}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n学科: {subject}\n\n{msg.content}"
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"[文本] 已保存: {filepath}")

    def _save_image(self, msg, save_dir: Path):
        """保存图片"""
        try:
            path = msg.download(dir_path=str(save_dir), timeout=30)
            if path and not isinstance(path, str) and hasattr(path, 'name'):
                self.logger.info(f"[图片] 已保存: {path}")
            elif path:
                self.logger.info(f"[图片] 已保存: {path}")
        except Exception as e:
            self.logger.error(f"图片下载失败: {e}")

    def _save_video(self, msg, save_dir: Path):
        """保存视频"""
        try:
            path = msg.download(dir_path=str(save_dir), timeout=60)
            if path:
                self.logger.info(f"[视频] 已保存: {path}")
        except Exception as e:
            self.logger.error(f"视频下载失败: {e}")

    def _save_voice(self, msg, save_dir: Path):
        """保存语音 + 可选转文字"""
        try:
            path = msg.download(dir_path=str(save_dir), timeout=30)
            if path:
                self.logger.info(f"[语音] 已保存: {path}")
            
            # 语音转文字
            if self.config.get('voice_to_text', {}).get('enabled', False):
                try:
                    text = msg.to_text()
                    if text:
                        txt_path = Path(path).with_suffix('.txt') if path else save_dir / f"{msg.sender}_voice.txt"
                        txt_path.write_text(f"发送者: {msg.sender}\n语音转文字:\n{text}", encoding='utf-8')
                        self.logger.info(f"[语音转文字] 已保存: {txt_path}")
                except Exception as e:
                    self.logger.warning(f"语音转文字失败: {e}")
        except Exception as e:
            self.logger.error(f"语音下载失败: {e}")

    def _save_file(self, msg, save_dir: Path):
        """保存文件"""
        try:
            # 优先用 download_to 指定文件名
            filename = getattr(msg, 'file_name', f"{msg.sender}_{datetime.now().strftime('%H%M%S')}")
            filepath = save_dir / filename
            result = msg.download_to(str(filepath))
            if result:
                self.logger.info(f"[文档] 已保存: {filepath}")
            else:
                # 备用方案
                path = msg.download(dir_path=str(save_dir), force_click=True, timeout=30)
                if path:
                    self.logger.info(f"[文档] 已保存: {path}")
        except Exception as e:
            self.logger.error(f"文档下载失败: {e}")

    def _save_note(self, msg, save_dir: Path):
        """保存笔记 (含图片、文件、视频等)"""
        try:
            # 保存笔记中的所有文件
            result = msg.save_files(dir_path=str(save_dir))
            if result and hasattr(result, 'data') and result.data:
                for f in result.data:
                    self.logger.info(f"[笔记文件] 已保存: {f}")
            
            # 保存笔记文本内容为 markdown
            md_path = save_dir / f"note_{msg.sender}_{datetime.now().strftime('%H%M%S')}.md"
            try:
                md_content = msg.to_markdown(dir_path=str(save_dir))
                if md_content:
                    md_path.write_text(md_content, encoding='utf-8')
                    self.logger.info(f"[笔记MD] 已保存: {md_path}")
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"笔记保存失败: {e}")

    def _save_link(self, msg, save_dir: Path):
        """保存链接消息"""
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"link_{msg.sender}_{timestamp}.txt"
        filepath = save_dir / filename
        content = f"发送者: {msg.sender}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n链接内容:\n{msg.content}"
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"[链接] 已保存: {filepath}")

    def _listen_group(self, group_name: str):
        """为指定群添加监听"""
        try:
            def callback(msg, chat):
                self._process_message(msg, group_name)
            
            self.wx.AddListenChat(nickname=group_name, callback=callback)
            self.listened_chats[group_name] = True
            self.logger.info(f"开始监听群: {group_name}")
        except Exception as e:
            self.logger.error(f"监听群失败 [{group_name}]: {e}")

    def _check_new_messages(self):
        """主动轮询检查新消息 (备用方案，配合监听使用)"""
        if not self._is_in_schedule_window():
            return
        
        for group_cfg in self.config['groups']:
            group_name = group_cfg['name']
            try:
                self.wx.ChatWith(group_name)
                msgs = self.wx.GetAllMessage(savepic=False, savefile=False, savevoice=False)
                for msg in msgs:
                    self._process_message(msg, group_name)
            except Exception as e:
                self.logger.error(f"轮询检查失败 [{group_name}]: {e}")

    def start(self):
        """启动机器人"""
        self.logger.info("=" * 50)
        self.logger.info("作业下载机器人启动中...")
        self.logger.info("=" * 50)
        
        if not self._init_wechat():
            return
        
        # 为每个配置的群添加监听
        for group_cfg in self.config['groups']:
            self._listen_group(group_cfg['name'])
        
        # 添加定时任务: 在时间窗口内定期轮询 (双重保障)
        sched_cfg = self.config['schedule']
        self.scheduler.add_job(
            self._check_new_messages,
            CronTrigger(
                hour=f"{sched_cfg['start_hour']}-{sched_cfg['end_hour']}",
                minute=f"*/{max(1, sched_cfg['poll_interval_seconds'] // 60)}",
                timezone="Asia/Shanghai"
            ),
            id='poll_messages',
            replace_existing=True
        )
        
        # 每天清理去重缓存
        self.scheduler.add_job(
            lambda: self.last_msg_hash.clear(),
            CronTrigger(hour=0, minute=0, timezone="Asia/Shanghai"),
            id='clear_hash_cache'
        )
        
        self.scheduler.start()
        self.logger.info(f"调度器已启动，监听时间窗口: {sched_cfg['start_hour']}:{sched_cfg['start_minute']:02d}-{sched_cfg['end_hour']}:{sched_cfg['end_minute']:02d}")
        self.logger.info("按 Ctrl+C 停止")
        
        try:
            # wxauto的 KeepRunning 会阻塞主线程处理监听回调
            self.wx.KeepRunning()
        except KeyboardInterrupt:
            self.logger.info("收到停止信号")
        finally:
            self.stop()

    def stop(self):
        """停止机器人"""
        self.logger.info("正在停止...")
        self.scheduler.shutdown(wait=False)
        for group_name in self.listened_chats:
            try:
                self.wx.RemoveListenChat(nickname=group_name)
            except Exception:
                pass
        self.logger.info("已停止")


def main():
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        print(f"配置文件不存在: {config_path}")
        sys.exit(1)
    
    bot = HomeworkBot(str(config_path))
    bot.start()


if __name__ == "__main__":
    main()