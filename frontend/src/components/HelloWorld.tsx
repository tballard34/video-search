import { TbSearch } from "react-icons/tb";

import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

function HelloWorld() {
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="flex items-center justify-center gap-2">
            <TbSearch className="h-6 w-6 text-primary" />
            Video Search
          </CardTitle>
          <p className="text-sm text-foreground-secondary">Search and explore video content with semantic embeddings.</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-center">
            <p className="text-sm text-foreground-secondary">Built with:</p>
            <div className="flex flex-wrap justify-center gap-2 text-xs">
              <span className="rounded bg-primary/10 px-2 py-1 text-primary">React</span>
              <span className="rounded bg-primary/10 px-2 py-1 text-primary">TypeScript</span>
              <span className="rounded bg-primary/10 px-2 py-1 text-primary">Vite</span>
              <span className="rounded bg-primary/10 px-2 py-1 text-primary">Tailwind CSS</span>
              <span className="rounded bg-primary/10 px-2 py-1 text-primary">shadcn/ui</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default HelloWorld;
