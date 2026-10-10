import { QueryClient } from "@tanstack/react-query";

import { ApiError } from "./api-client";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      gcTime: 5 * 60_000,
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        // Don't retry client errors (4xx) or an unreachable backend.
        if (error instanceof ApiError && (error.status === 0 || error.status < 500))
          return false;
        return failureCount < 2;
      },
    },
  },
});
