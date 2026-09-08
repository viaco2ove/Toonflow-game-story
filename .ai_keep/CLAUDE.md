# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Toonflow-game-story

## 不允许随意放置测试和临时文档
测试脚本和文档和临时文档
只允许放置在.cache 文件夹下。

## git 提交限制
不允许自己commit 和push 到 git

## 不允许ai 修改的标注
文件第一行: @no_modify
或者 # @no_modify
或者 # no_modify

## 模型接口
你现在claude code cli 调用大模型，连接了ccrg 模型路由
每次请求的 必须包含 workflow_stage 字段
ccrg 识别:{workflow_stage:analyze_plan}
intention_analyze: 返回{workflow_stage:analyze_plan} 等。
客户端发送内容包含：
- "{workflow_stage:intention_analyze}": 分析用户意图阶段
- "{workflow_stage:execute_solve}"": 执行解决方案阶段
- "{workflow_stage:analyze_plan}"": 分析执行结果阶段
- "{workflow_stage:execute_write}"": 写入结果阶段

流程：intention_analyze → execute_solve → analyze_plan → execute_write
