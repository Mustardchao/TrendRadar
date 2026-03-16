# -*- coding: utf-8 -*-
"""
TrendRadar 飞书推送模块
发送热点数据到飞书群聊（卡片格式）
"""

import requests
import json
import os
from datetime import datetime


def format_trends_message(trends):
    """格式化热点数据为消息内容"""
    content_lines = ["[TrendRadar 热点监控]\n"]
    
    if trends and len(trends) > 0:
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        content_lines.insert(1, f"更新时间：{update_time}\n")
        
        for i, t in enumerate(trends[:10], 1):
            platform = t.get('platform', '未知')
            keyword = t.get('keyword', '未知')
            heat = t.get('heat_score', t.get('heat', 0))
            content_lines.append(f"{i}. [{platform}] {keyword} - 热度 {heat}")
        
        content_lines.append("\n数据每小时自动更新")
    else:
        content_lines.append("暂无热点数据")
    
    return content_lines


def send_to_feishu(webhook_url, trends):
    """发送飞书消息 - 卡片格式（interactive）"""
    
    content_lines = format_trends_message(trends)
    
    data = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "[TrendRadar 热点监控]"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": "\n".join(content_lines)
                }
            ]
        }
    }
    
    try:
        response = requests.post(webhook_url, json=data, timeout=10)
        result = response.json()
        
        if result.get('code') == 0:
            print("[OK] Feishu push successful")
            return True
        else:
            print(f"[ERROR] Feishu push failed: {result}")
            return False
    except Exception as e:
        print(f"[ERROR] Feishu push exception: {e}")
        return False


def main():
    """主函数 - 从环境变量获取配置"""
    
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')
    
    if not webhook_url:
        print("[ERROR] FEISHU_WEBHOOK_URL not set")
        return False
    
    trends_file = 'docs/api/trends.json'
    trends = []
    
    try:
        with open(trends_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            trends = data.get('trends', [])
        print(f"[INFO] Loaded {len(trends)} trends from {trends_file}")
    except Exception as e:
        print(f"[WARNING] Could not load trends: {e}")
        trends = []
    
    success = send_to_feishu(webhook_url, trends)
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
