function generateNews() {
    const category = document.getElementById('category').value;
    const keywords = document.getElementById('keywords').value;
    
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category, keywords })
    })
    .then(response => response.json())
    .then(data => {
        const output = document.getElementById('news-output');
        output.innerHTML = data.news.map(item => 
            `<article class="news-item">
                <span class="category-tag">${item.category}</span>
                <h2>${item.title}</h2>
                <p class="news-content">${item.content}</p>
                <div class="news-date">${new Date().toLocaleString()}</div>
            </article>`
        ).join('') + '<button id="load-more-btn" class="btn btn-secondary mt-3 w-100">生成更多</button>';
        
        // 为新生成的按钮添加事件监听
        document.getElementById('load-more-btn').addEventListener('click', function() {
            fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ category, keywords })
            })
            .then(response => response.json())
            .then(data => {
                const newArticles = data.news.map(item =>
                    `<article class="news-item">
                        <span class="category-tag">${item.category}</span>
                        <h2>${item.title}</h2>
                        <p class="news-content">${item.content}</p>
                        <div class="news-date">${new Date().toLocaleString()}</div>
                    </article>`
                ).join('');
                // 在生成更多按钮之前插入新的新闻
                const loadMoreBtn = document.getElementById('load-more-btn');
                loadMoreBtn.insertAdjacentHTML('beforebegin', newArticles);
            });
        });
    });
}

// 初始化加载时生成示例新闻
document.addEventListener('DOMContentLoaded', generateNews);