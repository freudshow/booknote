#问题分析与特征识别
from typing import List, Dict, Set, Tuple, Optional, Any
from enum import Enum
import math
from collections import defaultdict, deque
import heapq
import random

class ProblemType(Enum):
    """问题类型分类"""
    OPTIMIZATION = "最优化问题"
    DECISION = "决策问题"
    SEARCH = "搜索问题"
    COUNTING = "计数问题"
    CONSTRUCTION = "构造问题"

class ProblemCharacteristics:
    """问题特征分析"""
   
    def __init__(self, problem_description: str):
        self.description = problem_description
        self.features = self._analyze_features()
        
    def _analyze_features(self) -> Dict[str, Any]:
        """分析问题特征"""
        features = {
            'problem_type': self._classify_problem_type(),
            'constraints': self._extract_constraints(),
            'objective': self._identify_objective(),
            'structure': self._analyze_structure(),
            'size_characteristics': self._estimate_size()
        }
        return features
   
    def _classify_problem_type(self) -> ProblemType:
        """分类问题类型"""
        desc_lower = self.description.lower()
        
        if any(word in desc_lower for word in ['最大', '最小', '最优', '最佳']):
            return ProblemType.OPTIMIZATION
        elif any(word in desc_lower for word in ['是否', '存在', '判断']):
            return ProblemType.DECISION
        elif any(word in desc_lower for word in ['找到', '寻找', '搜索']):
            return ProblemType.SEARCH
        elif any(word in desc_lower for word in ['多少', '计数', '数量']):
            return ProblemType.COUNTING
        else:
            return ProblemType.CONSTRUCTION
   
    def suggest_algorithm_strategy(self) -> List[str]:
        """基于特征推荐算法策略"""
        strategies = []
        
        if self.features['problem_type'] == ProblemType.OPTIMIZATION:
            if self._has_optimal_substructure():
                strategies.extend(['动态规划', '贪心算法'])
            if self._has_recursive_structure():
                strategies.append('分治算法')
               
        if self.features['problem_type'] == ProblemType.SEARCH:
            strategies.extend(['回溯搜索', '分支限界', '启发式搜索'])
            
        if self._is_np_hard():
            strategies.extend(['近似算法', '局部搜索', '元启发式'])
            
        return strategies
   
    def _has_optimal_substructure(self) -> bool:
        """检查是否具有最优子结构"""
        # 通过关键词分析
        keywords = ['子问题', '递推', '阶段', '状态转移']
        return any(keyword in self.description for keyword in keywords)
   
    def _has_recursive_structure(self) -> bool:
        """检查是否具有递归结构"""
        keywords = ['递归', '分解', '合并', '划分']
        return any(keyword in self.description for keyword in keywords)
   
    def _is_np_hard(self) -> bool:
        """初步判断是否为NP难问题"""
        hard_keywords = ['组合', '排列', '旅行商', '背包', '调度']
        return any(keyword in self.description for keyword in hard_keywords)

class AlgorithmStrategySelector:
    """算法策略选择器"""
   
    def __init__(self):
        self.strategy_mapping = {
            '分治算法': ['归并排序', '快速排序', '最近点对'],
            '动态规划': ['背包问题', '最长公共子序列', '矩阵链乘法'],
            '贪心算法': ['最小生成树', '霍夫曼编码', '活动选择'],
            '回溯搜索': ['八皇后', '数独', '图着色'],
            '启发式搜索': ['A*算法', '最佳优先搜索']
        }
        
    def select_strategy(self, problem: ProblemCharacteristics,
                       constraints: Dict[str, Any]) -> str:
        """选择最优算法策略"""
        candidate_strategies = problem.suggest_algorithm_strategy()
        
        # 基于约束过滤
        filtered_strategies = self._filter_by_constraints(
            candidate_strategies, constraints)
        
        # 评分选择
        scored_strategies = []
        for strategy in filtered_strategies:
            score = self._score_strategy(strategy, problem, constraints)
            scored_strategies.append((strategy, score))
            
        # 返回最高分策略
        return max(scored_strategies, key=lambda x: x[1])[0]
   
    def _filter_by_constraints(self, strategies: List[str],
                             constraints: Dict[str, Any]) -> List[str]:
        """基于约束过滤策略"""
        valid_strategies = []
        
        for strategy in strategies:
            if self._strategy_satisfies_constraints(strategy, constraints):
                valid_strategies.append(strategy)
               
        return valid_strategies
   
    def _strategy_satisfies_constraints(self, strategy: str,
                                      constraints: Dict[str, Any]) -> bool:
        """检查策略是否满足约束"""
        time_limit = constraints.get('time_limit', float('inf'))
        space_limit = constraints.get('space_limit', float('inf'))
        
        # 策略的复杂度特征
        complexity = self._get_strategy_complexity(strategy)
        
        return (complexity['time'] <= time_limit and
                complexity['space'] <= space_limit)
   
    def _get_strategy_complexity(self, strategy: str) -> Dict[str, float]:
        """获取策略的复杂度特征"""
        complexities = {
            '分治算法': {'time': math.log, 'space': math.log},
            '动态规划': {'time': lambda n: n**2, 'space': lambda n: n**2},
            '贪心算法': {'time': lambda n: n*math.log(n), 'space': lambda n: n},
            '回溯搜索': {'time': lambda n: 2**n, 'space': lambda n: n}
        }
        return complexities.get(strategy, {'time': lambda n: n**3, 'space': lambda n: n**2})
#算法设计模式复制
class AlgorithmDesignPattern:
    """算法设计模式"""
   
    @staticmethod
    def divide_and_conquer_template(problem: Any, base_case: Callable,
                                  divide: Callable, combine: Callable) -> Any:
        """分治算法模板"""
        if base_case(problem):
            return base_case(problem)
        
        # 分解问题
        subproblems = divide(problem)
        
        # 递归解决子问题
        solutions = []
        for subproblem in subproblems:
            solution = AlgorithmDesignPattern.divide_and_conquer_template(
                subproblem, base_case, divide, combine)
            solutions.append(solution)
        
        # 合并结果
        return combine(solutions)
   
    @staticmethod
    def dynamic_programming_template(problem: Any, state_definition: Callable,
                                  transition: Callable, initialization: Callable) -> Any:
        """动态规划模板"""
        # 定义状态空间
        states = state_definition(problem)
        n = len(states)
        
        # 初始化DP表
        dp = initialization(states)
        
        # 状态转移
        for i in range(1, n):
            for j in range(len(states[i])):
                dp[i][j] = transition(dp, i, j, states)
        
        # 提取最优解
        return dp[-1][-1]
   
    @staticmethod
    def greedy_algorithm_template(elements: List[Any],
                                selection: Callable,
                                feasibility: Callable,
                                solution_check: Callable) -> List[Any]:
        """贪心算法模板"""
        solution = []
        remaining = sorted(elements, key=selection)  # 按贪心准则排序
        
        while remaining and not solution_check(solution):
            # 选择当前最优元素
            candidate = remaining.pop(0)
            
            if feasibility(solution, candidate):
                solution.append(candidate)
        
        return solution
   
    @staticmethod
    def backtracking_template(solution: List[Any], candidates: List[Any],
                            is_valid: Callable, is_complete: Callable) -> List[List[Any]]:
        """回溯搜索模板"""
        solutions = []
        
        def backtrack(current_solution, available_candidates):
            if is_complete(current_solution):
                solutions.append(current_solution.copy())
                return
            
            for candidate in available_candidates:
                if is_valid(current_solution, candidate):
                    # 做出选择
                    current_solution.append(candidate)
                    new_candidates = [c for c in available_candidates if c != candidate]
                    
                    # 递归探索
                    backtrack(current_solution, new_candidates)
                    
                    # 撤销选择
                    current_solution.pop()
        
        backtrack(solution, candidates)
        return solutions

class ProblemSolvingFramework:
    """问题解决框架"""
   
    def __init__(self):
        self.phases = [
            '问题理解', '特征分析', '策略选择',
            '算法设计', '实现优化', '验证测试'
        ]
   
    def solve_problem(self, problem_description: str,
                     input_data: Any, constraints: Dict[str, Any]) -> Any:
        """系统化问题解决流程"""
        # 阶段1: 问题理解
        problem_type = ProblemCharacteristics(problem_description)
        
        # 阶段2: 特征分析
        features = problem_type.features
        
        # 阶段3: 策略选择
        selector = AlgorithmStrategySelector()
        strategy = selector.select_strategy(problem_type, constraints)
        
        # 阶段4: 算法设计
        algorithm = self._design_algorithm(strategy, features)
        
        # 阶段5: 实现优化
        optimized_algorithm = self._optimize_implementation(algorithm, constraints)
        
        # 阶段6: 验证测试
        solution = optimized_algorithm(input_data)
        self._validate_solution(solution, problem_description)
        
        return solution
   
    def _design_algorithm(self, strategy: str, features: Dict[str, Any]) -> Callable:
        """设计具体算法"""
        if strategy == '分治算法':
            return self._design_divide_conquer(features)
        elif strategy == '动态规划':
            return self._design_dynamic_programming(features)
        elif strategy == '贪心算法':
            return self._design_greedy(features)
        else:
            return self._design_general(features)
   
    def _validate_solution(self, solution: Any, problem_description: str) -> bool:
        """验证解决方案"""
        # 根据问题描述验证解的正确性
        if '最大' in problem_description:
            return self._is_optimal(solution, problem_description)
        elif '存在' in problem_description:
            return solution is not None
        else:
            return True  # 简化验证

class AlgorithmicThinking:
    """算法思维训练"""
   
    def __init__(self):
        self.thinking_models = [
            '递归思维', '归纳思维', '抽象思维', '分解思维', '模式识别'
        ]
   
    def develop_recursive_thinking(self, problem: Any) -> Any:
        """培养递归思维"""
        # 识别基本情况
        if self._is_base_case(problem):
            return self._solve_base_case(problem)
        
        # 问题分解
        subproblems = self._decompose_problem(problem)
        
        # 递归假设
        subsolutions = [self.develop_recursive_thinking(sp) for sp in subproblems]
        
        # 组合结果
        return self._combine_solutions(subsolutions)
   
    def pattern_recognition_training(self, problems: List[Any]) -> Dict[str, List[Any]]:
        """模式识别训练"""
        patterns = defaultdict(list)
        
        for problem in problems:
            # 提取问题特征
            features = self._extract_problem_features(problem)
            
            # 匹配已知模式
            matched_pattern = self._match_pattern(features)
            patterns[matched_pattern].append(problem)
        
        return patterns
   
    def abstract_thinking_development(self, concrete_problems: List[Any]) -> Any:
        """抽象思维发展"""
        # 从具体问题中抽象共性
        common_structure = self._find_common_structure(concrete_problems)
        
        # 构建抽象模型
        abstract_model = self._build_abstract_model(common_structure)
        
        # 应用抽象模型解决新问题
        return abstract_model