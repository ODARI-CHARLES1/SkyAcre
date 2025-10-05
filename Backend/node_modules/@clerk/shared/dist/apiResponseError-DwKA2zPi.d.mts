import { ClerkAPIResponseError as ClerkAPIResponseError$1, ClerkAPIError, ClerkAPIErrorJSON } from '@clerk/types';

interface ClerkAPIResponseOptions {
    data: ClerkAPIErrorJSON[];
    status: number;
    clerkTraceId?: string;
    retryAfter?: number;
}
declare class ClerkAPIResponseError extends Error implements ClerkAPIResponseError$1 {
    clerkError: true;
    status: number;
    message: string;
    clerkTraceId?: string;
    retryAfter?: number;
    errors: ClerkAPIError[];
    constructor(message: string, { data, status, clerkTraceId, retryAfter }: ClerkAPIResponseOptions);
    toString: () => string;
}

export { ClerkAPIResponseError as C };
