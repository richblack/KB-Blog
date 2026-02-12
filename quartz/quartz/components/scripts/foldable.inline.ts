// Foldable Lists Toggle Script
// 規則：所有有子列表的項目都可摺疊（圖片除外），預設展開

document.addEventListener("nav", () => {
    // 選取所有有子列表的列表項目
    const allListItems = document.querySelectorAll("article li");

    allListItems.forEach((li) => {
        const htmlLi = li as HTMLElement;

        // 檢查是否有子列表
        const hasNestedList = li.querySelector(":scope > ul, :scope > ol");
        if (!hasNestedList) return;

        // 檢查是否包含圖片 (圖片項目不摺疊)
        const hasImage = li.querySelector(":scope > img");
        if (hasImage) return;

        // 避免 SPA 導航後重複綁定
        if (htmlLi.dataset.foldableInit === "true") return;
        htmlLi.dataset.foldableInit = "true";

        htmlLi.addEventListener("click", (e: Event) => {
            const target = e.target as HTMLElement;

            // 避免點擊連結時觸發
            if (target.tagName === 'A') return;

            // 避免點擊子列表內的項目時觸發父層收合
            const targetLi = target.closest('li');
            if (targetLi !== li) return;

            e.stopPropagation();
            // 切換 collapsed 狀態 (預設展開，點擊收合)
            htmlLi.classList.toggle("collapsed");
        });
    });
});
