/**
 * Logseq 知識工作者增強系統 Pro 版
 * 
 * 更新日誌：
 * 1. 排除代碼區塊：現在位於 `inline-code` 或 ```code-block``` 內的語法將被忽略。
 * 2. 提升穩定性：改用非破壞性的節點替換法，解決染色失效或變黑粗體的問題。
 * 3. 性能優化：精準定位文字節點，減少瀏覽器負擔。
 */

console.log('[Knowledge Worker] Pro System Initializing...');

function debounce(fn, delay) {
    let timeoutId;
    return function (...args) {
        if (timeoutId) clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

/**
 * 核心處理邏輯：遍歷文字節點並替換語法
 */
function processTextNodes() {
    // 找出所有區塊內容，排除編輯中的區塊
    const containers = document.querySelectorAll('.block-content:not(:has(textarea))');
    const regex = /\?\?([tb])\/(.+?):(.+?)\?\?/g;
    const colorMap = { 'r': 'ls-bg-r', 'o': 'ls-bg-o', 'y': 'ls-bg-y', 'g': 'ls-bg-g', 't': 'ls-bg-t', 's': 'ls-bg-s', 'b': 'ls-bg-b', 'p': 'ls-bg-p', 'i': 'ls-bg-i', 'a': 'ls-bg-a', 'k': 'ls-bg-k' };
    const textColorMap = { 'r': 'ls-text-r', 'o': 'ls-text-o', 'y': 'ls-text-y', 'g': 'ls-text-g', 't': 'ls-text-t', 's': 'ls-text-s', 'b': 'ls-text-b', 'p': 'ls-text-p', 'i': 'ls-text-i', 'a': 'ls-text-a' };

    containers.forEach(container => {
        // 使用 TreeWalker 找出所有純文字節點
        const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
            acceptNode: function(node) {
                // 排除代碼塊、代碼行、編輯器組件
                if (node.parentElement.closest('code, pre, .cm-content, textarea, style, script')) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        });

        let node;
        const nodesToReplace = [];

        while (node = walker.nextNode()) {
            if (regex.test(node.textContent)) {
                nodesToReplace.push(node);
            }
            regex.lastIndex = 0; // 重置正則索引
        }

        // 執行替換
        nodesToReplace.forEach(textNode => {
            const content = textNode.textContent;
            const parent = textNode.parentNode;
            if (!parent) return;

            const fragment = document.createDocumentFragment();
            let lastIndex = 0;
            let match;

            while ((match = regex.exec(content)) !== null) {
                // 加上匹配前的文字
                if (match.index > lastIndex) {
                    fragment.appendChild(document.createTextNode(content.substring(lastIndex, match.index)));
                }

                const [fullMatch, type, rawColor, text] = match;
                let color = rawColor.replace(/<[^>]*>/g, '').trim();
                
                // 建立染色 Span
                const span = document.createElement('span');
                span.className = 'ls-custom-color';
                span.textContent = text;

                // 處理顏色與類別
                if (type === 't') {
                    if (textColorMap[color]) {
                        span.classList.add(textColorMap[color]);
                    } else {
                        if (/^[0-9a-fA-F]{3,6}$/.test(color)) color = '#' + color;
                        span.style.setProperty('color', color, 'important');
                    }
                } else {
                    span.classList.add('ls-color-bg-mode');
                    if (colorMap[color]) {
                        span.classList.add(colorMap[color]);
                    } else {
                        if (/^[0-9a-fA-F]{3,6}$/.test(color)) color = '#' + color;
                        span.style.setProperty('background-color', color, 'important');
                        span.style.setProperty('color', 'white', 'important');
                    }
                }

                fragment.appendChild(span);
                lastIndex = regex.lastIndex;
            }

            // 加上剩餘的文字
            if (lastIndex < content.length) {
                fragment.appendChild(document.createTextNode(content.substring(lastIndex)));
            }

            parent.replaceChild(fragment, textNode);
        });
    });
}

/**
 * 原有的區塊標籤 (++/) 染色邏輯
 */
async function applyBlockTagStyles() {
    processTextNodes(); // 執行行內染色

    try {
        if (!window.logseq || !window.logseq.api) return;
        const allBlocks = await window.logseq.api.datascript_query(`
            [:find ?uuid ?content
             :where [?b :block/uuid ?uuid] [?b :block/content ?content]]
        `);
        if (!allBlocks) return;
        const tagBlocks = allBlocks.filter(([_, content]) => 
            content && typeof content === 'string' && content.trim().startsWith('++/'));

        let css = '';
        tagBlocks.forEach(([uuid]) => {
            css += `.block-ref-wrap.inline:has([blockid="${uuid}"]):not(:has(.block-ref-wrap)) {
                background-color: #ff9800 !important;
                color: white !important;
                padding: 2px 12px !important;
                border-radius: 20px !important;
                display: inline-block !important;
                font-size: 0.75em !important;
                vertical-align: middle !important;
                line-height: 1.4 !important;
            }\n`;
        });

        const oldStyle = document.getElementById('auto-block-tags');
        if (oldStyle) oldStyle.remove();
        const style = document.createElement('style');
        style.id = 'auto-block-tags';
        style.textContent = css;
        document.head.appendChild(style);
    } catch (e) {}
}

const debouncedUpdate = debounce(applyBlockTagStyles, 800);

function init() {
    console.log('[Knowledge Worker] Pro System Active.');
    setTimeout(applyBlockTagStyles, 2000);
    
    const observer = new MutationObserver((mutations) => {
        let shouldUpdate = false;
        for (let mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                shouldUpdate = true;
                break;
            }
        }
        if (shouldUpdate) debouncedUpdate();
    });
    
    const appContainer = document.getElementById('app-container') || document.body;
    observer.observe(appContainer, { childList: true, subtree: true });
    
    // 定時同步備援 (減少頻率以優化性能)
    setInterval(applyBlockTagStyles, 20000);
}

if (document.readyState === 'complete') {
    init();
} else {
    window.addEventListener('load', init);
}
