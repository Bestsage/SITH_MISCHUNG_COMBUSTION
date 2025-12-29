"use client";

import { CalculationProvider } from "@/contexts/CalculationContext";

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <CalculationProvider>
            {children}
        </CalculationProvider>
    );
}
