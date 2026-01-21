"use client";

import { CalculationProvider } from "@/contexts/CalculationContext";
import { AuthProvider } from "@/components/auth";

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <AuthProvider>
            <CalculationProvider>
                {children}
            </CalculationProvider>
        </AuthProvider>
    );
}
