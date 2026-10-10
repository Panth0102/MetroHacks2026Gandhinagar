import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-center">
      <p className="text-sm font-medium text-muted-foreground">404</p>
      <h2 className="text-xl font-semibold">Page not found</h2>
      <p className="max-w-sm text-sm text-muted-foreground">
        The page you are looking for does not exist in this dashboard.
      </p>
      <Link
        to="/"
        className="mt-2 inline-flex h-10 items-center rounded-md bg-accent px-4 text-sm font-medium text-accent-foreground hover:bg-accent/90"
      >
        Back to overview
      </Link>
    </div>
  );
}
