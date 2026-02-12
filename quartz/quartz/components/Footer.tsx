import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/footer.scss"
import { version } from "../../package.json"
import { i18n } from "../i18n"

interface Options {
  links: Record<string, string>
}

export default ((opts?: Options) => {
  const Footer: QuartzComponent = ({ displayClass, cfg }: QuartzComponentProps) => {
    const year = new Date().getFullYear()
    const links = opts?.links ?? []
    return (
      <footer class={`${displayClass ?? ""}`}>
        <div style={{ marginBottom: "20px" }}>
          <script async data-uid="6784ee6d83" src="https://uncle6.kit.com/6784ee6d83/index.js"></script>
        </div>
        <p style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
          <span>六叔觀察站 Uncle6 Observatories © {year}</span>
          <span>|</span>
          <a href="https://www.facebook.com/U6Automatia/" target="_blank" rel="noopener noreferrer" style={{ display: "flex", alignItems: "center", gap: "5px", color: "inherit", textDecoration: "none" }}>
            <img src="https://upload.wikimedia.org/wikipedia/commons/b/b9/2023_Facebook_icon.svg" alt="Facebook" width="18" height="18" />
            <span>Leo自動症 Automatia</span>
          </a>
        </p>
      </footer>
    )
  }

  Footer.css = style
  return Footer
}) satisfies QuartzComponentConstructor
