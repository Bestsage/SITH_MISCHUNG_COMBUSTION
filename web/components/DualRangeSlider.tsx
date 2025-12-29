import { useCallback, useEffect, useState, useRef } from "react";
import clsx from "clsx";

interface DualRangeSliderProps {
    min: number;
    max: number;
    step?: number;
    value: [number, number];
    onChange: (value: [number, number]) => void;
    className?: string;
    color?: string;
}

export default function DualRangeSlider({ min, max, step = 1, value, onChange, className, color = "#00d4ff" }: DualRangeSliderProps) {
    const [minVal, maxVal] = value;
    const minValRef = useRef(minVal);
    const maxValRef = useRef(maxVal);
    const range = useRef<HTMLDivElement>(null);

    // Convert to percentage
    const getPercent = useCallback(
        (value: number) => Math.round(((value - min) / (max - min)) * 100),
        [min, max]
    );

    // Set width of the range to decrease from the left side
    useEffect(() => {
        const minPercent = getPercent(minVal);
        const maxPercent = getPercent(maxValRef.current);

        if (range.current) {
            range.current.style.left = `${minPercent}%`;
            range.current.style.width = `${maxPercent - minPercent}%`;
        }
    }, [minVal, getPercent]);

    // Set width of the range to decrease from the right side
    useEffect(() => {
        const minPercent = getPercent(minValRef.current);
        const maxPercent = getPercent(maxVal);

        if (range.current) {
            range.current.style.width = `${maxPercent - minPercent}%`;
        }
    }, [maxVal, getPercent]);

    return (
        <div className={clsx("relative w-full h-8 flex items-center", className)}>
            <style jsx>{`
                input[type=range]::-webkit-slider-thumb {
                    background-color: ${color};
                }
            `}</style>
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={minVal}
                onChange={(event) => {
                    const value = Math.min(Number(event.target.value), maxVal - step);
                    onChange([value, maxVal]);
                    minValRef.current = value;
                }}
                className={clsx(
                    "pointer-events-none absolute h-0 w-full outline-none z-[3]",
                    "appearance-none",
                    "[&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-50",
                    "bg-transparent"
                )}
                style={{ zIndex: minVal > max - 100 ? "5" : "3" }}
            />
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={maxVal}
                onChange={(event) => {
                    const value = Math.max(Number(event.target.value), minVal + step);
                    onChange([minVal, value]);
                    maxValRef.current = value;
                }}
                className={clsx(
                    "pointer-events-none absolute h-0 w-full outline-none z-[4]",
                    "appearance-none",
                    "[&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-50",
                    "bg-transparent"
                )}
            />

            <div className="relative w-full">
                <div className="absolute w-full h-1 bg-[#27272a] rounded z-[1]" />
                <div ref={range} className="absolute h-1 rounded z-[2]" style={{ backgroundColor: color }} />
            </div>
        </div>
    );
}
