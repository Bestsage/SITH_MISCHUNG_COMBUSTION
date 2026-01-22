"use client";

import { CalculationProvider } from "@/contexts/CalculationContext";
import { AuthProvider } from "@/components/auth";
import { ThemeProvider } from "@/contexts/ThemeContext";

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <AuthProvider>
            <ThemeProvider>
                <CalculationProvider>
                    {children}
                </CalculationProvider>
            </ThemeProvider>
        </AuthProvider>
    );
}
