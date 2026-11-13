"use client";

import { useEffect, useRef } from "react";

declare global {
  interface Window {
    turnstile?: {
      render: (element: HTMLElement, options: { sitekey: string; callback: (token: string) => void }) => string;
      remove: (id: string) => void;
    };
  }
}

export function Turnstile({ onToken }: { onToken: (token: string) => void }) {
  const siteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;
  const holder = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!siteKey || !holder.current) return;
    let widgetId = "";
    let script: HTMLScriptElement | null = null;
    const render = () => {
      if (!holder.current || !window.turnstile || widgetId) return;
      widgetId = window.turnstile.render(holder.current, { sitekey: siteKey, callback: onToken });
    };
    if (window.turnstile) {
      render();
    } else {
      script = document.createElement("script");
      script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      script.async = true;
      script.onload = render;
      document.body.appendChild(script);
    }
    return () => {
      if (widgetId && window.turnstile) window.turnstile.remove(widgetId);
      if (script) script.remove();
    };
  }, [onToken, siteKey]);

  if (!siteKey) return null;
  return <div ref={holder} className="min-h-16" />;
}
