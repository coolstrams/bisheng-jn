import React, { forwardRef } from "react";
import { cname } from "@/components/bs-ui/utils";
import Upvote from "./upvote.svg?react";
import Upvoted from "./upvoted.svg?react";
import Hot from "./hot.svg?react";

export const UpvoteIcon = forwardRef<
    SVGSVGElement & { className: any },
    React.PropsWithChildren<{ className?: string }>
>(({className, ...props}, ref) => {
    return <Upvote ref={ref} className={cname('text-[#9CA3BA]', className)} {...props} />;
});

export const UpvotedIcon = forwardRef<
    SVGSVGElement & { className: any },
    React.PropsWithChildren<{ className?: string }>
>(({className, ...props}, ref) => {
    return <Upvoted ref={ref} className={cname('text-[#9CA3BA]', className)} {...props} />;
});

export const HotIcon = forwardRef<
    SVGSVGElement & { className: any },
    React.PropsWithChildren<{ className?: string }>
>(({className, ...props}, ref) => {
    return <Hot ref={ref} className={cname('text-[#9CA3BA]', className)} {...props} />;
});