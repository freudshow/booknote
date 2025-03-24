import json
import pandas as pd

# The JSON data provided in the query
json_data = '''
{
  "Pad": {
    "TotalYcCount": 70,
    "TotalYxCount": 5,
    "TotalYkCount": 10,
    "TotalDDCount": 0,
    "TotalParameterCount": 0,
    "YcRatioEnable": 1,
    "RecordingYkOpera": 0,
    "LinkAddr": 1,
    "SingleORDoubleInit": 0,
    "LinkAddrLen": 2,
    "VsqLen": 1,
    "coTlen": 2,
    "AsduLen": 2,
    "InfoAddrLen": 3,
    "YxType": 1,
    "YcType": 13,
    "DdType": 206,
    "YkType": 45,
    "T0TimeOut": 30,
    "T1TimeOut": 30,
    "T2TimeOut": 12,
    "T3TimeOut": 20,
    "k": 12,
    "w": 8,
    "baseyear": 2000,
    "alldatainterval": 0,
    "allddinterval": 0,
    "setclockinterval": 0,
    "testlinkinterval": 0,
    "encrypt": 0,
    "sendcos": 1,
    "BackScan": 0,
    "ThreadAfterSndDelayms": 100,
    "ThreadAfterRcvDelayms": 100
  },
  "ParaInstruction": "v0.1运用园区",
  "Para": [
    {
      "SN": 0,
      "Running_info": [],
      "Actionfixed_info": []
    }
  ],
  "FaultEventSubmission": [],
  "YCDataItem": [
    {
      "No": 0,
      "Name": "设备[1]-市电线电压Vab",
      "Unit": null,
      "Addr": 16385,
      "Xishu": 1.0,
      "RealDevNo": 562,
      "type": 1,
      "Idx": 0
    },
    {
      "No": 1,
      "Name": "设备[1]-市电线电压Vbc",
      "Unit": null,
      "Addr": 16386,
      "Xishu": 1.0,
      "RealDevNo": 563,
      "type": 1,
      "Idx": 1
    },
    {
      "No": 2,
      "Name": "设备[1]-市电线电压Vca",
      "Unit": null,
      "Addr": 16387,
      "Xishu": 1.0,
      "RealDevNo": 564,
      "type": 1,
      "Idx": 2
    },
    {
      "No": 3,
      "Name": "设备[1]-市电频率",
      "Unit": null,
      "Addr": 16388,
      "Xishu": 1.0,
      "RealDevNo": 557,
      "type": 1,
      "Idx": 3
    },
    {
      "No": 4,
      "Name": "设备[1]-市电相电流Ia",
      "Unit": null,
      "Addr": 16389,
      "Xishu": 1.0,
      "RealDevNo": 558,
      "type": 1,
      "Idx": 4
    },
    {
      "No": 5,
      "Name": "设备[1]-市电相电流Ib",
      "Unit": null,
      "Addr": 16390,
      "Xishu": 1.0,
      "RealDevNo": 559,
      "type": 1,
      "Idx": 5
    },
    {
      "No": 6,
      "Name": "设备[1]-市电相电流Ic",
      "Unit": null,
      "Addr": 16391,
      "Xishu": 1.0,
      "RealDevNo": 560,
      "type": 1,
      "Idx": 6
    },
    {
      "No": 7,
      "Name": "设备[1]-市电地线电流",
      "Unit": null,
      "Addr": 16392,
      "Xishu": 1.0,
      "RealDevNo": 561,
      "type": 1,
      "Idx": 7
    },
    {
      "No": 8,
      "Name": "设备[1]-市电总有功功率",
      "Unit": null,
      "Addr": 16393,
      "Xishu": 1.0,
      "RealDevNo": 556,
      "type": 1,
      "Idx": 8
    },
    {
      "No": 9,
      "Name": "设备[1]-发电线电压Vab",
      "Unit": null,
      "Addr": 16394,
      "Xishu": 1.0,
      "RealDevNo": 550,
      "type": 1,
      "Idx": 9
    },
    {
      "No": 10,
      "Name": "设备[1]-发电线电压Vbc",
      "Unit": null,
      "Addr": 16395,
      "Xishu": 1.0,
      "RealDevNo": 551,
      "type": 1,
      "Idx": 10
    },
    {
      "No": 11,
      "Name": "设备[1]-发电线电压Vca",
      "Unit": null,
      "Addr": 16396,
      "Xishu": 1.0,
      "RealDevNo": 552,
      "type": 1,
      "Idx": 11
    },
    {
      "No": 12,
      "Name": "设备[1]-发电相电压Va",
      "Unit": null,
      "Addr": 16397,
      "Xishu": 1.0,
      "RealDevNo": 553,
      "type": 1,
      "Idx": 12
    },
    {
      "No": 13,
      "Name": "设备[1]-发电相电压Vb",
      "Unit": null,
      "Addr": 16398,
      "Xishu": 1.0,
      "RealDevNo": 554,
      "type": 1,
      "Idx": 13
    },
    {
      "No": 14,
      "Name": "设备[1]-发电相电压Vc",
      "Unit": null,
      "Addr": 16399,
      "Xishu": 1.0,
      "RealDevNo": 555,
      "type": 1,
      "Idx": 14
    },
    {
      "No": 15,
      "Name": "设备[1]-发电频率",
      "Unit": null,
      "Addr": 16400,
      "Xishu": 1.0,
      "RealDevNo": 545,
      "type": 1,
      "Idx": 15
    },
    {
      "No": 16,
      "Name": "设备[1]-发电相电流Ia",
      "Unit": null,
      "Addr": 16401,
      "Xishu": 1.0,
      "RealDevNo": 546,
      "type": 1,
      "Idx": 16
    },
    {
      "No": 17,
      "Name": "设备[1]-发电相电流Ib",
      "Unit": null,
      "Addr": 16402,
      "Xishu": 1.0,
      "RealDevNo": 547,
      "type": 1,
      "Idx": 17
    },
    {
      "No": 18,
      "Name": "设备[1]-发电相电流Ic",
      "Unit": null,
      "Addr": 16403,
      "Xishu": 1.0,
      "RealDevNo": 548,
      "type": 1,
      "Idx": 18
    },
    {
      "No": 19,
      "Name": "设备[1]-发电地线电流",
      "Unit": null,
      "Addr": 16404,
      "Xishu": 1.0,
      "RealDevNo": 549,
      "type": 1,
      "Idx": 19
    },
    {
      "No": 20,
      "Name": "设备[1]-发电总有功功率",
      "Unit": null,
      "Addr": 16405,
      "Xishu": 1.0,
      "RealDevNo": 531,
      "type": 1,
      "Idx": 20
    },
    {
      "No": 21,
      "Name": "设备[1]-发电总逆功率",
      "Unit": null,
      "Addr": 16406,
      "Xishu": 1.0,
      "RealDevNo": 532,
      "type": 1,
      "Idx": 21
    },
    {
      "No": 22,
      "Name": "设备[1]-发电总无功功率",
      "Unit": null,
      "Addr": 16407,
      "Xishu": 1.0,
      "RealDevNo": 536,
      "type": 1,
      "Idx": 22
    },
    {
      "No": 23,
      "Name": "设备[1]-发电总视在功率",
      "Unit": null,
      "Addr": 16408,
      "Xishu": 1.0,
      "RealDevNo": 540,
      "type": 1,
      "Idx": 23
    },
    {
      "No": 24,
      "Name": "设备[1]-发电A相功率因数",
      "Unit": null,
      "Addr": 16409,
      "Xishu": 1.0,
      "RealDevNo": 541,
      "type": 1,
      "Idx": 24
    },
    {
      "No": 25,
      "Name": "设备[1]-发电B相功率因数",
      "Unit": null,
      "Addr": 16410,
      "Xishu": 1.0,
      "RealDevNo": 542,
      "type": 1,
      "Idx": 25
    },
    {
      "No": 26,
      "Name": "设备[1]-发电C相功率因数",
      "Unit": null,
      "Addr": 16411,
      "Xishu": 1.0,
      "RealDevNo": 543,
      "type": 1,
      "Idx": 26
    },
    {
      "No": 27,
      "Name": "设备[1]-发电总功率因数",
      "Unit": null,
      "Addr": 16412,
      "Xishu": 1.0,
      "RealDevNo": 544,
      "type": 1,
      "Idx": 27
    },
    {
      "No": 28,
      "Name": "设备[1]-当前发电有功百分比",
      "Unit": null,
      "Addr": 16413,
      "Xishu": 1.0,
      "RealDevNo": 519,
      "type": 1,
      "Idx": 28
    },
    {
      "No": 29,
      "Name": "设备[1]-当前发电无功百分比",
      "Unit": null,
      "Addr": 16414,
      "Xishu": 1.0,
      "RealDevNo": 520,
      "type": 1,
      "Idx": 29
    },
    {
      "No": 30,
      "Name": "设备[1]-当前转速",
      "Unit": null,
      "Addr": 16415,
      "Xishu": 1.0,
      "RealDevNo": 524,
      "type": 1,
      "Idx": 30
    },
    {
      "No": 31,
      "Name": "设备[1]-转速拾取1",
      "Unit": null,
      "Addr": 16416,
      "Xishu": 1.0,
      "RealDevNo": 525,
      "type": 1,
      "Idx": 31
    },
    {
      "No": 32,
      "Name": "设备[1]-转速拾取2",
      "Unit": null,
      "Addr": 16417,
      "Xishu": 1.0,
      "RealDevNo": 526,
      "type": 1,
      "Idx": 32
    },
    {
      "No": 33,
      "Name": "设备[1]-发动机启动失败次数",
      "Unit": null,
      "Addr": 16418,
      "Xishu": 1.0,
      "RealDevNo": 529,
      "type": 1,
      "Idx": 33
    },
    {
      "No": 34,
      "Name": "设备[1]-当前预热时间",
      "Unit": null,
      "Addr": 16419,
      "Xishu": 1.0,
      "RealDevNo": 530,
      "type": 1,
      "Idx": 34
    },
    {
      "No": 35,
      "Name": "设备[0]-冷却水温度",
      "Unit": null,
      "Addr": 16420,
      "Xishu": 1.0,
      "RealDevNo": 584,
      "type": 1,
      "Idx": 35
    },
    {
      "No": 36,
      "Name": "设备[0]-机油温度",
      "Unit": null,
      "Addr": 16421,
      "Xishu": 1.0,
      "RealDevNo": 585,
      "type": 1,
      "Idx": 36
    },
    {
      "No": 37,
      "Name": "设备[1]-机油压力",
      "Unit": null,
      "Addr": 16422,
      "Xishu": 1.0,
      "RealDevNo": 510,
      "type": 1,
      "Idx": 37
    },
    {
      "No": 38,
      "Name": "设备[1]-燃油液位",
      "Unit": null,
      "Addr": 16423,
      "Xishu": 1.0,
      "RealDevNo": 511,
      "type": 1,
      "Idx": 38
    },
    {
      "No": 39,
      "Name": "设备[1]-冷却水液位",
      "Unit": null,
      "Addr": 16424,
      "Xishu": 1.0,
      "RealDevNo": 512,
      "type": 1,
      "Idx": 39
    },
    {
      "No": 40,
      "Name": "设备[1]-起动电流",
      "Unit": null,
      "Addr": 16425,
      "Xishu": 1.0,
      "RealDevNo": 518,
      "type": 1,
      "Idx": 40
    },
    {
      "No": 41,
      "Name": "设备[1]-故障码遥测 1952",
      "Unit": null,
      "Addr": 16426,
      "Xishu": 1.0,
      "RealDevNo": 492,
      "type": 1,
      "Idx": 41
    },
    {
      "No": 42,
      "Name": "设备[1]-故障码遥测 1953",
      "Unit": null,
      "Addr": 16427,
      "Xishu": 1.0,
      "RealDevNo": 493,
      "type": 1,
      "Idx": 42
    },
    {
      "No": 43,
      "Name": "设备[1]-故障码遥测 1954",
      "Unit": null,
      "Addr": 16428,
      "Xishu": 1.0,
      "RealDevNo": 494,
      "type": 1,
      "Idx": 43
    },
    {
      "No": 44,
      "Name": "设备[1]-故障码遥测 1955",
      "Unit": null,
      "Addr": 16429,
      "Xishu": 1.0,
      "RealDevNo": 495,
      "type": 1,
      "Idx": 44
    },
    {
      "No": 45,
      "Name": "设备[1]-故障码遥测 1956",
      "Unit": null,
      "Addr": 16430,
      "Xishu": 1.0,
      "RealDevNo": 496,
      "type": 1,
      "Idx": 45
    },
    {
      "No": 46,
      "Name": "设备[1]-故障码遥测 1957",
      "Unit": null,
      "Addr": 16431,
      "Xishu": 1.0,
      "RealDevNo": 497,
      "type": 1,
      "Idx": 46
    },
    {
      "No": 47,
      "Name": "设备[1]-故障码遥测 1958",
      "Unit": null,
      "Addr": 16432,
      "Xishu": 1.0,
      "RealDevNo": 498,
      "type": 1,
      "Idx": 47
    },
    {
      "No": 48,
      "Name": "设备[1]-故障码遥测 1959",
      "Unit": null,
      "Addr": 16433,
      "Xishu": 1.0,
      "RealDevNo": 499,
      "type": 1,
      "Idx": 48
    },
    {
      "No": 49,
      "Name": "设备[1]-故障码遥测 1960",
      "Unit": null,
      "Addr": 16434,
      "Xishu": 1.0,
      "RealDevNo": 500,
      "type": 1,
      "Idx": 49
    },
    {
      "No": 50,
      "Name": "设备[1]-故障码遥测 1961",
      "Unit": null,
      "Addr": 16435,
      "Xishu": 1.0,
      "RealDevNo": 501,
      "type": 1,
      "Idx": 50
    },
    {
      "No": 51,
      "Name": "设备[1]-故障码遥测 1962",
      "Unit": null,
      "Addr": 16436,
      "Xishu": 1.0,
      "RealDevNo": 502,
      "type": 1,
      "Idx": 51
    },
    {
      "No": 52,
      "Name": "设备[1]-故障码遥测 1963",
      "Unit": null,
      "Addr": 16437,
      "Xishu": 1.0,
      "RealDevNo": 503,
      "type": 1,
      "Idx": 52
    },
    {
      "No": 53,
      "Name": "设备[1]-故障码遥测 1964",
      "Unit": null,
      "Addr": 16438,
      "Xishu": 1.0,
      "RealDevNo": 504,
      "type": 1,
      "Idx": 53
    },
    {
      "No": 54,
      "Name": "设备[1]-故障码遥测 1965",
      "Unit": null,
      "Addr": 16439,
      "Xishu": 1.0,
      "RealDevNo": 505,
      "type": 1,
      "Idx": 54
    },
    {
      "No": 55,
      "Name": "设备[1]-故障码遥测 1966",
      "Unit": null,
      "Addr": 16440,
      "Xishu": 1.0,
      "RealDevNo": 506,
      "type": 1,
      "Idx": 55
    },
    {
      "No": 56,
      "Name": "设备[1]-故障码遥测 1967",
      "Unit": null,
      "Addr": 16441,
      "Xishu": 1.0,
      "RealDevNo": 507,
      "type": 1,
      "Idx": 56
    },
    {
      "No": 57,
      "Name": "设备[0]-备用遥测7",
      "Unit": null,
      "Addr": 16442,
      "Xishu": 1.0,
      "RealDevNo": 61,
      "type": 1,
      "Idx": 57
    },
    {
      "No": 58,
      "Name": "设备[0]-备用遥测8",
      "Unit": null,
      "Addr": 16443,
      "Xishu": 1.0,
      "RealDevNo": 62,
      "type": 1,
      "Idx": 58
    },
    {
      "No": 59,
      "Name": "设备[0]-备用遥测10",
      "Unit": null,
      "Addr": 16444,
      "Xishu": 1.0,
      "RealDevNo": 64,
      "type": 1,
      "Idx": 59
    },
    {
      "No": 60,
      "Name": "设备[2]-备用遥测11",
      "Unit": null,
      "Addr": 16445,
      "Xishu": 1.0,
      "RealDevNo": 144,
      "type": 1,
      "Idx": 60
    },
    {
      "No": 61,
      "Name": "设备[2]-备用遥测12",
      "Unit": null,
      "Addr": 16446,
      "Xishu": 1.0,
      "RealDevNo": 145,
      "type": 1,
      "Idx": 61
    },
    {
      "No": 62,
      "Name": "设备[2]-备用遥测13",
      "Unit": null,
      "Addr": 16447,
      "Xishu": 1.0,
      "RealDevNo": 146,
      "type": 1,
      "Idx": 62
    },
    {
      "No": 63,
      "Name": "设备[2]-备用遥测14",
      "Unit": null,
      "Addr": 16448,
      "Xishu": 1.0,
      "RealDevNo": 147,
      "type": 1,
      "Idx": 63
    },
    {
      "No": 64,
      "Name": "设备[1]-Uan相电压",
      "Unit": null,
      "Addr": 16449,
      "Xishu": 1.0,
      "RealDevNo": 571,
      "type": 1,
      "Idx": 64
    },
    {
      "No": 65,
      "Name": "设备[1]-Ubn相电压",
      "Unit": null,
      "Addr": 16450,
      "Xishu": 1.0,
      "RealDevNo": 572,
      "type": 1,
      "Idx": 65
    },
    {
      "No": 66,
      "Name": "设备[1]-Ucn相电压",
      "Unit": null,
      "Addr": 16451,
      "Xishu": 1.0,
      "RealDevNo": 573,
      "type": 1,
      "Idx": 66
    },
    {
      "No": 67,
      "Name": "设备[1]-A相电流",
      "Unit": null,
      "Addr": 16452,
      "Xishu": 1.0,
      "RealDevNo": 575,
      "type": 1,
      "Idx": 67
    },
    {
      "No": 68,
      "Name": "设备[1]-B相电流",
      "Unit": null,
      "Addr": 16453,
      "Xishu": 1.0,
      "RealDevNo": 576,
      "type": 1,
      "Idx": 68
    },
    {
      "No": 69,
      "Name": "设备[1]-C相电流",
      "Unit": null,
      "Addr": 16454,
      "Xishu": 1.0,
      "RealDevNo": 577,
      "type": 1,
      "Idx": 69
    }
  ],
  "YXDataItem": [
    {
      "No": 0,
      "Name": "设备[0]-发电机运行中",
      "Unit": null,
      "Addr": 1,
      "Xishu": 1.0,
      "RealDevNo": 598,
      "type": 0,
      "Idx": 0
    },
    {
      "No": 1,
      "Name": "设备[0]-虚拟遥信1",
      "Unit": null,
      "Addr": 2,
      "Xishu": 1.0,
      "RealDevNo": 30,
      "type": 0,
      "Idx": 1
    },
    {
      "No": 2,
      "Name": "设备[0]-虚拟遥信2",
      "Unit": null,
      "Addr": 3,
      "Xishu": 1.0,
      "RealDevNo": 31,
      "type": 0,
      "Idx": 2
    },
    {
      "No": 3,
      "Name": "设备[0]-虚拟遥信3",
      "Unit": null,
      "Addr": 4,
      "Xishu": 1.0,
      "RealDevNo": 32,
      "type": 0,
      "Idx": 3
    },
    {
      "No": 4,
      "Name": "设备[0]-ZMW45-3H断路器分合状态",
      "Unit": null,
      "Addr": 5,
      "Xishu": 1.0,
      "RealDevNo": 601,
      "type": 0,
      "Idx": 4
    }
  ],
  "YKDataItem": [
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 2,
      "No": 0,
      "Name": "设备[1]-设备自身遥控1",
      "Unit": null,
      "Addr": 24577,
      "RealDevNo": 1,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 1,
      "No": 1,
      "Name": "设备[1]-设备自身遥控1",
      "Unit": null,
      "Addr": 24577,
      "RealDevNo": 1,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 3,
      "No": 2,
      "Name": "设备[1]-预留设备自身遥控5",
      "Unit": null,
      "Addr": 24578,
      "RealDevNo": 5,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 0,
      "No": 3,
      "Name": "设备[1]-预留设备自身遥控6",
      "Unit": null,
      "Addr": 24578,
      "RealDevNo": 6,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 3,
      "No": 4,
      "Name": "设备[1]-预留设备自身遥控7",
      "Unit": null,
      "Addr": 24579,
      "RealDevNo": 7,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 0,
      "No": 5,
      "Name": "设备[1]-预留设备自身遥控8",
      "Unit": null,
      "Addr": 24579,
      "RealDevNo": 8,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 3,
      "No": 6,
      "Name": "设备[1]-预留设备自身遥控9",
      "Unit": null,
      "Addr": 24580,
      "RealDevNo": 9,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 0,
      "No": 7,
      "Name": "设备[1]-预留设备自身遥控10",
      "Unit": null,
      "Addr": 24580,
      "RealDevNo": 10,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 2,
      "No": 8,
      "Name": "设备[0]-下挂遥控108",
      "Unit": null,
      "Addr": 24581,
      "RealDevNo": 108,
      "type": 2,
      "Idx": 0
    },
    {
      "$type": "LTU.SelectedYkTable, 边缘网关维护软件",
      "Xishu": 0.0,
      "YkValue": 1,
      "No": 9,
      "Name": "设备[0]-下挂遥控109",
      "Unit": null,
      "Addr": 24581,
      "RealDevNo": 109,
      "type": 2,
      "Idx": 0
    }
  ],
  "DDDataItem": []
}
'''

# Parse the JSON string into a Python dictionary
data = json.loads(json_data)

# Extract each section from the dictionary
pad_data = data['Pad']
para_instruction = data['ParaInstruction']
para_data = data['Para']
fault_event_data = data['FaultEventSubmission']
yc_data = data['YCDataItem']
yx_data = data['YXDataItem']
yk_data = data['YKDataItem']
dd_data = data['DDDataItem']

# Convert each section into a pandas DataFrame
pad_df = pd.DataFrame([pad_data])  # Single object, wrap in list for one-row DataFrame
para_instruction_df = pd.DataFrame({'ParaInstruction': [para_instruction]})  # Single string
para_df = pd.DataFrame(para_data)  # List with one object
fault_event_df = pd.DataFrame(fault_event_data)  # Empty list
yc_data_df = pd.DataFrame(yc_data)  # List of objects
yx_data_df = pd.DataFrame(yx_data)  # List of objects
yk_data_df = pd.DataFrame(yk_data)  # List of objects
dd_data_df = pd.DataFrame(dd_data)  # Empty list

# Write all DataFrames to an Excel file, each on a separate sheet
with pd.ExcelWriter('output.xlsx') as writer:
    pad_df.to_excel(writer, sheet_name='Pad', index=False)
    para_instruction_df.to_excel(writer, sheet_name='ParaInstruction', index=False)
    para_df.to_excel(writer, sheet_name='Para', index=False)
    fault_event_df.to_excel(writer, sheet_name='FaultEventSubmission', index=False)
    yc_data_df.to_excel(writer, sheet_name='YCDataItem', index=False)
    yx_data_df.to_excel(writer, sheet_name='YXDataItem', index=False)
    yk_data_df.to_excel(writer, sheet_name='YKDataItem', index=False)
    dd_data_df.to_excel(writer, sheet_name='DDDataItem', index=False)

print("Excel file 'output.xlsx' has been created successfully.")