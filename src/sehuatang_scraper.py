# src/sehuatang_scraper.py
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote

class SeHuaTangScraper:
    def __init__(self, config):
        self.base_url = config['base_url']
        self.search_path = config['search_path']
        self.timeout = config.get('timeout', 30)
        self.headers = {
            'User-Agent': config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    def search(self, keyword):
        """搜索番号并返回结果"""
        encoded_keyword = quote(keyword)
        search_url = f"{self.base_url}{self.search_path}{encoded_keyword}"
        
        try:
            response = requests.get(
                search_url, 
                headers=self.headers, 
                timeout=self.timeout
            )
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return self._parse_results(response.text)
            else:
                return {'error': f'搜索失败，状态码: {response.status_code}'}
        except Exception as e:
            return {'error': f'搜索请求异常: {str(e)}'}
    
    def _parse_results(self, html):
        """解析搜索结果页面"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # 查找帖子列表
        threads = soup.select('tbody[id^="normalthread_"]')
        
        for thread in threads[:20]:  # 限制最多20个结果
            try:
                # 标题和链接
                title_elem = thread.select_one('a.s.xst')
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"{self.base_url}/{link.lstrip('/')}"
                
                # 作者
                author_elem = thread.select_one('td.by cite a')
                author = author_elem.text.strip() if author_elem else '未知'
                
                # 回复/查看
                meta = thread.select_one('td.num a')
                if meta:
                    meta_text = meta.text.strip()
                    replies, views = self._parse_meta(meta_text)
                else:
                    replies = views = 0
                
                # 最后发表
                last_post_elem = thread.select_one('td.by em a')
                last_post_time = last_post_elem.text.strip() if last_post_elem else '未知'
                
                # 磁力链接（需要进入帖子页面获取）
                # 这里先返回帖子链接，前端可以点击查看
                
                results.append({
                    'title': title,
                    'link': link,
                    'author': author,
                    'replies': replies,
                    'views': views,
                    'last_post': last_post_time,
                    'has_magnet': False  # 需要后续获取
                })
            except Exception as e:
                continue
        
        return {'results': results, 'total': len(results)}
    
    def _parse_meta(self, meta_text):
        """解析回复/查看数字"""
        try:
            parts = meta_text.split('/')
            replies = int(re.search(r'\d+', parts[0]).group()) if len(parts) > 0 else 0
            views = int(re.search(r'\d+', parts[1]).group()) if len(parts) > 1 else 0
            return replies, views
        except:
            return 0, 0
