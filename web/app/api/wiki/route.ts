import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
    try {
        // Define wiki directory path - look in archive_python/wiki
        const wikiDir = path.join(process.cwd(), "..", "archive_python", "wiki");
        
        // Ordered list of wiki files to concatenate
        const wikiFiles = [
            "Home.md",
            "Partie-1-Les-Bases.md",
            "1-Introduction.md",
            "2-Tuyere-de-Laval.md",
            "3-Probleme-Thermique.md",
            "4-Refroidissement-Regeneratif.md",
            "Partie-2-Theorie-Avancee.md",
            "5-Chimie-Combustion.md",
            "Partie-3-Materiaux.md",
            "9-Criteres-Selection.md",
            "Partie-4-Guide-Logiciel.md",
            "Partie-5-Documentation-Technique.md",
            "13-Concepts-Fondamentaux.md",
        ];

        let combinedContent = "";

        for (const fileName of wikiFiles) {
            const filePath = path.join(wikiDir, fileName);
            try {
                if (fs.existsSync(filePath)) {
                    const content = fs.readFileSync(filePath, "utf-8");
                    combinedContent += content + "\n\n---\n\n";
                }
            } catch (err) {
                console.error(`Error reading ${fileName}:`, err);
            }
        }

        // If no ordered files found, try to read all .md files in directory
        if (!combinedContent) {
            try {
                const files = fs.readdirSync(wikiDir).filter(f => f.endsWith(".md"));
                for (const file of files) {
                    const filePath = path.join(wikiDir, file);
                    const content = fs.readFileSync(filePath, "utf-8");
                    combinedContent += content + "\n\n---\n\n";
                }
            } catch (err) {
                console.error("Error reading wiki directory:", err);
            }
        }

        if (!combinedContent) {
            return new NextResponse(
                "# Wiki\n\nAucun contenu wiki trouvé. Vérifiez que les fichiers markdown existent dans le dossier wiki.",
                { 
                    status: 200,
                    headers: { "Content-Type": "text/plain; charset=utf-8" }
                }
            );
        }

        return new NextResponse(combinedContent, {
            status: 200,
            headers: { "Content-Type": "text/plain; charset=utf-8" }
        });
    } catch (error) {
        console.error("Wiki API error:", error);
        return new NextResponse(
            "# Erreur\n\nImpossible de charger le contenu du wiki.",
            { 
                status: 500,
                headers: { "Content-Type": "text/plain; charset=utf-8" }
            }
        );
    }
}
