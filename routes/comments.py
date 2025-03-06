from flask import Blueprint, request, jsonify, session
from datetime import datetime
import os

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/add_comment', methods=['POST'])
def add_comment():
    if 'username' not in session:
        return jsonify({'error': '请先登录'}), 401
    
    event_id = request.form.get('event_id')
    comment_text = request.form.get('comment')
    
    if not event_id or not comment_text:
        return jsonify({'error': '缺少必要参数'}), 400
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    comment_line = f"{event_id}|{session['username']}|{comment_text}|{timestamp}\n"
    
    try:
        with open('comments.txt', 'a', encoding='utf-8') as f:
            f.write(comment_line)
        return jsonify({
            'username': session['username'],
            'comment': comment_text,
            'timestamp': timestamp
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comments_bp.route('/delete_comment', methods=['POST'])
def delete_comment():
    if 'username' not in session:
        return jsonify({'error': '请先登录'}), 401
    
    event_id = request.form.get('event_id')
    timestamp = request.form.get('timestamp')
    
    if not event_id or not timestamp:
        return jsonify({'error': '缺少必要参数'}), 400
    
    try:
        # 读取所有评论
        with open('comments.txt', 'r', encoding='utf-8') as f:
            comments = f.readlines()
        
        # 过滤掉要删除的评论
        new_comments = []
        for comment in comments:
            parts = comment.strip().split('|')
            if len(parts) >= 4:
                if not (parts[0] == event_id and 
                        parts[1] == session['username'] and 
                        parts[3] == timestamp):
                    new_comments.append(comment)
        
        # 写回文件
        with open('comments.txt', 'w', encoding='utf-8') as f:
            f.writelines(new_comments)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500