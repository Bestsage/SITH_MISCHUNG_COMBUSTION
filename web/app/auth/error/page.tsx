"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

const errorMessages: Record<string, string> = {
    Configuration: "Il y a un problème de configuration du serveur.",
    AccessDenied: "Accès refusé. Vous n'avez pas la permission d'accéder.",
    Verification: "Le lien de vérification a expiré ou a déjà été utilisé.",
    Default: "Une erreur inattendue s'est produite.",
    OAuthSignin: "Erreur lors de la création du lien OAuth.",
    OAuthCallback: "Erreur lors du retour du fournisseur OAuth.",
    OAuthCreateAccount: "Impossible de créer un compte avec ce fournisseur.",
    EmailCreateAccount: "Impossible de créer un compte avec cet email.",
    Callback: "Erreur dans le callback d'authentification.",
    OAuthAccountNotLinked: "Cet email est déjà associé à un autre compte.",
    EmailSignin: "Erreur lors de l'envoi de l'email de connexion.",
    CredentialsSignin: "Identifiants incorrects.",
    SessionRequired: "Veuillez vous connecter pour accéder à cette page.",
};

function ErrorContent() {
    const searchParams = useSearchParams();
    const error = searchParams.get("error") || "Default";
    const message = errorMessages[error] || errorMessages.Default;

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
            <div className="w-full max-w-md text-center">
                {/* Error Icon */}
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/10 border border-red-500/30 mb-6">
                    <svg className="w-10 h-10 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>

                <h1 className="text-2xl font-bold text-white mb-3">
                    Erreur d&apos;authentification
                </h1>

                <p className="text-slate-400 mb-8">
                    {message}
                </p>

                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <Link
                        href="/auth/signin"
                        className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium rounded-xl transition-all duration-200 shadow-lg shadow-cyan-500/25"
                    >
                        Réessayer
                    </Link>
                    <Link
                        href="/"
                        className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-xl transition-colors border border-slate-700"
                    >
                        Retour à l&apos;accueil
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default function AuthErrorPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="w-8 h-8 border-4 border-red-500 border-t-transparent rounded-full animate-spin" />
            </div>
        }>
            <ErrorContent />
        </Suspense>
    );
}
