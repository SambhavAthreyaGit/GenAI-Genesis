import "react";

declare global {
  namespace JSX {
    interface IntrinsicElements {
      "kicanvas-embed": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          src?: string;
          controls?: string;
          theme?: string;
        },
        HTMLElement
      >;
    }
  }
}

export {};
