import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"
// @ts-ignore
import script from "./scripts/comments.inline"

type Options = {
  provider: "giscus"
  options: {
    repo: `${string}/${string}`
    repoId: string
    category: string
    categoryId: string
    themeUrl?: string
    lightTheme?: string
    darkTheme?: string
    mapping?: "url" | "title" | "og:title" | "specific" | "number" | "pathname"
    strict?: boolean
    reactionsEnabled?: boolean
    inputPosition?: "top" | "bottom"
    lang?: string
  }
}

function boolToStringBool(b: boolean): string {
  return b ? "1" : "0"
}

export default ((opts: Options) => {
  const Comments: QuartzComponent = ({ displayClass, fileData }: QuartzComponentProps) => {
    // check if comments should be displayed according to frontmatter
    const disableComment: boolean =
      typeof fileData.frontmatter?.comments !== "undefined" &&
      (!fileData.frontmatter?.comments || fileData.frontmatter?.comments === "false")
    if (disableComment) {
      return <></>
    }

    return (
      <div class={classNames(displayClass, "giscus")} style={{ marginTop: "2rem", textAlign: "center" }}>
        <p style={{ fontWeight: "bold", opacity: 0.7 }}>這是一份「數位花園」筆記，內容隨時在生長。</p>
        <p>因應技術門檻，本站不開放留言。</p>
        <a
          href="https://www.facebook.com/U6Automatia/"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "inline-block",
            padding: "10px 20px",
            backgroundColor: "#4267B2", // Facebook Blue
            color: "white",
            borderRadius: "5px",
            textDecoration: "none",
            fontWeight: "bold",
            marginTop: "10px"
          }}
        >
          前往 Facebook 粉絲專頁討論 💬
        </a>
      </div>
    )
  }

  Comments.afterDOMLoaded = script

  return Comments
}) satisfies QuartzComponentConstructor<Options>
