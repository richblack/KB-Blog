import os
from datetime import datetime
from typing import List
from ..contracts.types import Article, PublisherConfig
from ..actions.utils import get_safe_path_elements

def generate_archive(articles: List[Article], config: PublisherConfig):
    year_map = {}
    
    for art in articles:
        date_str = str(art.date) if art.date else "1970-01-01"
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            dt = datetime(1970, 1, 1)
            
        y = dt.strftime("%Y")
        m = dt.strftime("%m")
        
        if y not in year_map: year_map[y] = {}
        if m not in year_map[y]: year_map[y][m] = []
        
        year_map[y][m].append(art)
        
    lines = [
        "---",
        "title: 文章歸檔",
        "layout: page",
        "---",
        "",
        "# 📅 歷史文章",
        "> 依照年份與月份整理",
        ""
    ]
    
    sorted_years = sorted(year_map.keys(), reverse=True)
    
    for y in sorted_years:
        is_open = ' open' if y == sorted_years[0] else ''
        lines.append(f'<details{is_open}>')
        lines.append(f'<summary><h2 style="display:inline-block">{y} 年</h2></summary>')
        lines.append('<div style="margin-left: 20px">')
        
        sorted_months = sorted(year_map[y].keys(), reverse=True)
        for m in sorted_months:
            count = len(year_map[y][m])
            lines.append('<details open>') 
            lines.append(f'<summary><h3 style="display:inline-block">{m} 月 ({count} 篇)</h3></summary>')
            lines.append('<div style="margin-left: 20px">') 
            lines.append('') 
            
            arts = year_map[y][m]
            arts.sort(key=lambda x: str(x.date), reverse=True)
            
            for art in arts:
                date = str(art.date)
                title = art.title
                safe_cat, safe_title = get_safe_path_elements(title, art.categories)
                lines.append(f"- {date} - [[{safe_title}|{title}]]")
                
            lines.append('')
            lines.append('</div>')
            lines.append("</details>")
            lines.append("")
        
        lines.append('</div>')
        lines.append('</details>')
        lines.append("")
    
    target_path = os.path.join(config.quartz_content_dir, "archive.md")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  📅 已生成歸檔頁面: archive.md")

def generate_tags_page(articles: List[Article], config: PublisherConfig):
    tag_map = {}
    
    for art in articles:
        for t in art.tags:
            if t not in tag_map:
                tag_map[t] = []
            tag_map[t].append(art)
            
    sorted_tags = sorted(tag_map.keys(), key=lambda x: x.lower())
    
    lines = [
        "---",
        "title: 標籤整理",
        "layout: page",
        "tags: []",
        "---",
        "",
        "# 🏷️ 標籤索引",
        "",
        "> 依照字母排序，點擊標籤查看相關文章",
        ""
    ]
    
    for tag in sorted_tags:
        arts = tag_map[tag]
        arts.sort(key=lambda x: str(x.date), reverse=True)
        
        lines.append('<details>')
        lines.append(f'<summary><h2 style="display:inline-block">#{tag} ({len(arts)} 篇)</h2></summary>')
        lines.append('<div style="margin-left: 20px">')
        lines.append('')

        for art in arts:
            title = art.title
            date = str(art.date)
            
            safe_cat, safe_title = get_safe_path_elements(title, art.categories)
            lines.append(f"- {date} - [[{safe_title}|{title}]]")
        
        lines.append('')
        lines.append('</div>')
        lines.append('</details>')
        lines.append("")

    target_path = os.path.join(config.quartz_content_dir, "all-tags.md")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  🏷️ 已生成標籤頁面: all-tags.md")
