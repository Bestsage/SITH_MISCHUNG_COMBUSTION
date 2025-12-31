"use client";

import { useState, useEffect, useMemo } from "react";
import AppLayout from "@/components/AppLayout";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

export default function WikiPage() {
    const [wikiContent, setWikiContent] = useState<string>("");
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        fetch("/api/wiki")
            .then(res => res.text())
            .then(content => {
                setWikiContent(content);
                setLoading(false);
            })
            .catch(() => {
                setLoading(false);
            });
    }, []);

    // Parse sections from wiki content
    const sections = useMemo(() => {
        const sectionList: { id: string; title: string; level: number }[] = [];
        const lines = wikiContent.split('\n');

        lines.forEach((line, index) => {
            const h2Match = line.match(/^## (\d+\..*)/);
            const h3Match = line.match(/^### (\d+\.\d+.*)/);

            if (h2Match) {
                sectionList.push({
                    id: `section-${index}`,
                    title: h2Match[1].trim(),
                    level: 2
                });
            } else if (h3Match) {
                sectionList.push({
                    id: `section-${index}`,
                    title: h3Match[1].trim(),
                    level: 3
                });
            }
        });

        return sectionList;
    }, [wikiContent]);

    // Filter content based on search
    const filteredContent = useMemo(() => {
        if (!searchQuery) return wikiContent;

        const lines = wikiContent.split('\n');
        const filteredLines: string[] = [];
        let includeSection = false;

        for (const line of lines) {
            if (line.startsWith('## ') || line.startsWith('### ')) {
                includeSection = line.toLowerCase().includes(searchQuery.toLowerCase());
            }
            if (includeSection || line.toLowerCase().includes(searchQuery.toLowerCase())) {
                filteredLines.push(line);
            }
        }

        return filteredLines.join('\n');
    }, [wikiContent, searchQuery]);

    return (
        <AppLayout>
            <div className="flex h-[calc(100vh-0px)] overflow-hidden">
                {/* Sidebar TOC - Fixed height with scroll */}
                <div className="w-80 bg-[#12121a] border-r border-[#27272a] flex flex-col h-full">
                    <div className="p-4 border-b border-[#27272a] flex-shrink-0">
                        <input
                            type="text"
                            placeholder="🔍 Rechercher dans le wiki..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="input-field text-sm"
                        />
                    </div>

                    <div className="flex-1 overflow-y-auto p-4">
                        <h3 className="text-xs font-bold text-[#a1a1aa] uppercase tracking-wider mb-3">
                            📑 Table des Matières ({sections.length})
                        </h3>
                        <div className="space-y-1">
                            {sections.map((section) => (
                                <button
                                    key={section.id}
                                    onClick={() => {
                                        document.getElementById(section.id)?.scrollIntoView({ behavior: 'smooth' });
                                    }}
                                    className={`w-full text-left px-2 py-1.5 rounded text-xs transition-all ${section.level === 3 ? 'ml-3 text-[#71717a]' : 'text-[#a1a1aa] font-medium'
                                        } hover:bg-[#1f1f2e] hover:text-white truncate`}
                                    title={section.title}
                                >
                                    {section.title.length > 35 ? section.title.substring(0, 35) + '...' : section.title}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Content - Isolated scroll */}
                <div className="flex-1 overflow-y-auto h-full">
                    {loading ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <span className="text-4xl animate-spin inline-block mb-4">⏳</span>
                                <p className="text-[#71717a]">Chargement du wiki...</p>
                            </div>
                        </div>
                    ) : wikiContent ? (
                        <div className="p-8 max-w-5xl mx-auto">
                            <div className="mb-6 bg-gradient-to-r from-[#00d4ff]/10 to-[#8b5cf6]/10 border border-[#27272a] rounded-xl p-6">
                                <h1 className="text-3xl font-bold text-white mb-2">📖 Wiki - Documentation Complète</h1>
                                <p className="text-[#71717a]">
                                    Guide de conception moteurs-fusées • {wikiContent.split('\n').length.toLocaleString()} lignes • LaTeX activé
                                </p>
                            </div>

                            <article className="wiki-content">
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm, remarkMath]}
                                    rehypePlugins={[rehypeKatex]}
                                    components={{
                                        h1: ({ children }) => (
                                            <h1 className="text-4xl font-bold text-white mt-12 mb-6 pb-4 border-b border-[#27272a]">
                                                {children}
                                            </h1>
                                        ),
                                        h2: ({ children, node }) => {
                                            const index = wikiContent.split('\n').findIndex(l => l.includes(String(children)));
                                            return (
                                                <h2 id={`section-${index}`} className="text-2xl font-bold text-[#00d4ff] mt-10 mb-4 scroll-mt-4">
                                                    {children}
                                                </h2>
                                            );
                                        },
                                        h3: ({ children, node }) => {
                                            const index = wikiContent.split('\n').findIndex(l => l.includes(String(children)));
                                            return (
                                                <h3 id={`section-${index}`} className="text-xl font-semibold text-[#8b5cf6] mt-8 mb-3 scroll-mt-4">
                                                    {children}
                                                </h3>
                                            );
                                        },
                                        h4: ({ children }) => (
                                            <h4 className="text-lg font-semibold text-[#f59e0b] mt-6 mb-2">
                                                {children}
                                            </h4>
                                        ),
                                        p: ({ children }) => (
                                            <p className="text-[#a1a1aa] mb-4 leading-relaxed">
                                                {children}
                                            </p>
                                        ),
                                        ul: ({ children }) => (
                                            <ul className="text-[#a1a1aa] mb-4 space-y-2 list-disc list-inside ml-4">
                                                {children}
                                            </ul>
                                        ),
                                        ol: ({ children }) => (
                                            <ol className="text-[#a1a1aa] mb-4 space-y-2 list-decimal list-inside ml-4">
                                                {children}
                                            </ol>
                                        ),
                                        li: ({ children }) => (
                                            <li className="text-[#a1a1aa]">{children}</li>
                                        ),
                                        code: ({ className, children }) => {
                                            const isInline = !className;
                                            if (isInline) {
                                                return (
                                                    <code className="bg-[#1a1a25] text-[#00d4ff] px-2 py-0.5 rounded font-mono text-sm">
                                                        {children}
                                                    </code>
                                                );
                                            }
                                            return (
                                                <code className="block bg-[#0a0a0f] text-[#a1a1aa] p-4 rounded-lg font-mono text-sm overflow-x-auto">
                                                    {children}
                                                </code>
                                            );
                                        },
                                        pre: ({ children }) => (
                                            <pre className="bg-[#0a0a0f] border border-[#27272a] rounded-lg p-4 overflow-x-auto my-4">
                                                {children}
                                            </pre>
                                        ),
                                        blockquote: ({ children }) => (
                                            <blockquote className="border-l-4 border-[#8b5cf6] bg-[#8b5cf6]/10 pl-4 py-2 my-4 rounded-r-lg">
                                                {children}
                                            </blockquote>
                                        ),
                                        table: ({ children }) => (
                                            <div className="overflow-x-auto my-6">
                                                <table className="w-full text-sm border border-[#27272a] rounded-lg overflow-hidden">
                                                    {children}
                                                </table>
                                            </div>
                                        ),
                                        thead: ({ children }) => (
                                            <thead className="bg-[#1a1a25]">{children}</thead>
                                        ),
                                        th: ({ children }) => (
                                            <th className="px-4 py-3 text-left text-[#a1a1aa] font-semibold border-b border-[#27272a]">
                                                {children}
                                            </th>
                                        ),
                                        td: ({ children }) => (
                                            <td className="px-4 py-3 text-[#a1a1aa] border-b border-[#27272a]/50">
                                                {children}
                                            </td>
                                        ),
                                        strong: ({ children }) => (
                                            <strong className="text-white font-semibold">{children}</strong>
                                        ),
                                        em: ({ children }) => (
                                            <em className="text-[#f59e0b]">{children}</em>
                                        ),
                                        hr: () => (
                                            <hr className="border-[#27272a] my-8" />
                                        ),
                                        a: ({ href, children }) => (
                                            <a href={href} className="text-[#00d4ff] hover:underline" target="_blank" rel="noopener noreferrer">
                                                {children}
                                            </a>
                                        ),
                                    }}
                                >
                                    {filteredContent}
                                </ReactMarkdown>
                            </article>
                        </div>
                    ) : (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <span className="text-5xl mb-4 block">❌</span>
                                <p className="text-[#ef4444]">Erreur: Impossible de charger wiki.md</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </AppLayout>
    );
}
