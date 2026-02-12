import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

interface Options {
    links: Record<string, string>
}

export default ((opts?: Options) => {
    const Navbar: QuartzComponent = ({ displayClass, cfg }: QuartzComponentProps) => {
        const links = opts?.links ?? []
        return (
            <nav class={`${displayClass ?? ""} navbar`}>
                <ul>
                    {Object.entries(links).map(([text, link]) => (
                        <li>
                            <a href={link}>{text}</a>
                        </li>
                    ))}
                </ul>
            </nav>
        )
    }

    Navbar.css = `
  .navbar ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    gap: 1.5rem;
    flex-direction: row;
  }
  
  .navbar a {
    color: var(--darkgray);
    text-decoration: none;
    font-weight: 700;
  }
  
  .navbar a:hover {
    color: var(--secondary);
    text-decoration: underline;
  }
  `

    return Navbar
}) satisfies QuartzComponentConstructor
