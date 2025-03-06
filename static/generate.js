document.addEventListener('DOMContentLoaded', function() {
    // 主题切换按钮事件处理
    document.getElementById('theme-toggle').addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        const icon = this.querySelector('i');
        if (icon.classList.contains('fa-moon')) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    });
    
    // 刷新按钮事件处理
    document.getElementById('refresh-btn').addEventListener('click', function() {
        const category = document.getElementById('category').value;
        const custom_word = document.getElementById('custom_word').value;
        const style = document.getElementById('style').value;
        
        fetch('/generate_one', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                category: category,
                custom_word: custom_word,
                style: style
            })
        })
        .then(response => response.json())
        .then(news => {
            const newsItem = createNewsElement(news);
            const newsList = document.getElementById('news-list');
            if (newsList.firstChild) {
                newsList.insertBefore(newsItem, newsList.firstChild);
            } else {
                newsList.appendChild(newsItem);
            }
        });
    });

    // 评论相关功能
    document.addEventListener('click', function(e) {
        // 删除评论按钮
        if (e.target.classList.contains('delete-comment-btn')) {
            const commentItem = e.target.closest('.comment-item');
            const listItem = e.target.closest('.list-group-item');
            const eventId = listItem.dataset.eventId;
            const timestamp = commentItem.dataset.timestamp;

            fetch('/comments/delete_comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    event_id: eventId,
                    timestamp: timestamp
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    commentItem.remove();
                } else {
                    alert(data.error || '删除失败');
                }
            });
        }

        // 添加评论按钮
        if (e.target.classList.contains('add-comment-btn')) {
            const listItem = e.target.closest('.list-group-item');
            const eventId = listItem.dataset.eventId;
            const commentInput = listItem.querySelector('.comment-input');
            const commentText = commentInput.value.trim();

            if (!commentText) {
                alert('请输入评论内容');
                return;
            }

            fetch('/comments/add_comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    event_id: eventId,
                    comment: commentText
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                const commentList = listItem.querySelector('.comment-list');
                const commentDiv = document.createElement('div');
                commentDiv.className = 'comment-item';
                commentDiv.dataset.timestamp = data.timestamp;
                commentDiv.innerHTML = `
                    <strong>${data.username}</strong> (${data.timestamp}): ${data.comment}
                    <button class="btn btn-sm btn-danger delete-comment-btn">删除</button>
                `;
                commentList.appendChild(commentDiv);
                commentInput.value = '';
            });
        }

        // 为所有生成后续按钮添加事件监听
        if (e.target.classList.contains('followup-btn')) {
            const listItem = e.target.closest('.list-group-item');
            const category = listItem.querySelector('strong').textContent.split(' ')[0];
            const style = listItem.querySelector('strong').textContent.match(/\((.*?)\)/)[1];
            
            fetch('/generate_one', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    category: category,
                    style: style,
                    is_follow_up: '1'
                })
            })
            .then(response => response.json())
            .then(news => {
                const newsItem = createNewsElement(news);
                listItem.insertAdjacentElement('afterend', newsItem);
            });
        }
    });

    // 朗读按钮事件处理
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('speak-btn')) {
            const listItem = e.target.closest('.list-group-item');
            const headline = listItem.querySelector('.news-story').textContent;
            const utterance = new SpeechSynthesisUtterance(headline);
            utterance.lang = 'zh-CN';
            speechSynthesis.speak(utterance);
        }
    });

    // 分享按钮事件处理
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('share-btn')) {
            const headline = e.target.dataset.headline;
            const tweetText = encodeURIComponent(headline);
            window.open(`https://twitter.com/intent/tweet?text=${tweetText}`, '_blank');
        }
    });

    // 投票按钮事件处理
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('vote-btn')) {
            const listItem = e.target.closest('.list-group-item');
            const eventId = listItem.dataset.eventId;
            const voteType = e.target.dataset.vote;
            const voteResult = listItem.querySelector('.vote-result');
            const currentVotes = voteResult.textContent.split('|').map(v => parseInt(v.match(/\d+/) || 0));
            
            if (voteType === 'believe') {
                currentVotes[0]++;
            } else {
                currentVotes[1]++;
            }
            
            voteResult.textContent = `相信：${currentVotes[0]} | 不相信：${currentVotes[1]}`;
        }
    });

    // 辅助函数：创建新闻元素
    function createNewsElement(news) {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        if (news.event_id) {
            li.dataset.eventId = news.event_id;
        }
        
        li.innerHTML = `
            <strong>${news.category} (${news.style})</strong>
            <div class="news-story">
                ${news.headline.split('\n').map(line => `<p>${line}</p>`).join('')}
            </div>
            <p class="image-desc text-muted">配图描述：${news.image_desc}</p>
            <p class="comment text-muted">网友评论：${news.comment}</p>
            <p class="heat text-muted">热度：${news.heat || '0'}</p>
            <p class="sentiment text-muted">情感：${news.sentiment || '中性'}</p>
            <div class="keywords mb-2">
                <span>关键词：</span>
                ${news.keywords ? news.keywords.map(keyword => 
                    `<span class="badge bg-primary keyword-badge" style="cursor: pointer;" data-keyword="${keyword}">${keyword}</span>`
                ).join('') : ''}
            </div>
            <button class="btn btn-sm btn-info followup-btn"><i class="fas fa-forward"></i> 后续新闻</button>
            <button class="btn btn-sm btn-primary speak-btn"><i class="fas fa-volume-up"></i> 朗读新闻</button>
            <button class="btn btn-sm btn-secondary share-btn" data-headline="${news.headline.split('\n')[0]}"><i class="fas fa-share"></i> 分享</button>
            <div class="voting mt-2">
                <span>你相信这条新闻吗？</span>
                <button class="btn btn-sm btn-success vote-btn" data-vote="believe">相信</button>
                <button class="btn btn-sm btn-danger vote-btn" data-vote="not_believe">不相信</button>
                <p class="vote-result">相信：${news.believe || 0} | 不相信：${news.not_believe || 0}</p>
            </div>
        `;
        
        return li;
    }
})