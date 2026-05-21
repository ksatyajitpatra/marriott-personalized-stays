"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import {
  ChevronDown,
  Globe,
  Heart,
  HelpCircle,
  Menu,
  Search,
  User,
  X,
} from "lucide-react";
import { useAuthStore } from "@/lib/auth-store";
import { cn } from "@/lib/utils";

/**
 * Top chrome that mimics marriott.com:
 *  - thin black utility bar (My Trips, Find Reservation, Help, Sign In)
 *  - white main bar with the Marriott logotype + primary nav
 *  - red Bonvoy account chip when signed in
 *  - a mobile drawer that mirrors the same nav
 */
export function MarriottHeader(): React.ReactElement {
  const pathname = usePathname();
  const router = useRouter();
  const guest = useAuthStore((s) => s.guest);
  const signOut = useAuthStore((s) => s.signOut);
  const [open, setOpen] = useState(false);

  const navItems: Array<{ href: string; label: string }> = [
    { href: "/", label: "Find & Reserve" },
    { href: "/search", label: "Hotels" },
    { href: "/trips", label: "My Trips" },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white">
      {/* Utility bar */}
      <div className="bg-[var(--color-bonvoy-ink)] text-white text-[12px]">
        <div className="mx-auto max-w-[1280px] px-4 sm:px-6 h-9 flex items-center justify-end gap-5">
          <Link
            href="/trips"
            className="hidden sm:inline-flex items-center gap-1.5 hover:text-white/80"
          >
            My Trips
          </Link>
          <Link
            href="/trips"
            className="hidden sm:inline-flex items-center gap-1.5 hover:text-white/80"
          >
            Find Reservation
          </Link>
          <span className="hidden sm:inline-flex items-center gap-1.5 text-white/70">
            <HelpCircle size={14} />
            Help
          </span>
          <span className="hidden sm:inline-flex items-center gap-1.5 text-white/70">
            <Globe size={14} />
            English
          </span>
          {guest ? (
            <button
              onClick={async () => {
                await signOut();
                router.push("/");
              }}
              className="inline-flex items-center gap-1.5 hover:text-white/80"
            >
              Sign Out
            </button>
          ) : (
            <Link
              href="/sign-in"
              className="inline-flex items-center gap-1.5 hover:text-white/80"
            >
              <User size={14} />
              Sign In or Join
            </Link>
          )}
        </div>
      </div>

      {/* Main bar */}
      <div className="border-b border-[var(--color-bonvoy-rule)] bg-white">
        <div className="mx-auto max-w-[1280px] px-4 sm:px-6 h-16 flex items-center gap-6">
          <button
            aria-label="Menu"
            className="md:hidden -ml-2 p-2"
            onClick={() => setOpen(true)}
          >
            <Menu size={22} />
          </button>

          <Link
            href="/"
            aria-label="Marriott Bonvoy home"
            className="flex items-center gap-2 mr-4"
          >
            <span className="font-serif text-[22px] tracking-[0.18em] font-light text-[var(--color-bonvoy-ink)]">
              MARRIOTT
            </span>
            <span className="hidden sm:inline-flex items-center text-[10px] tracking-[0.2em] uppercase text-[var(--color-bonvoy-muted)] border-l border-[var(--color-bonvoy-rule)] pl-3 ml-1">
              Bonvoy
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-7 text-[14px] text-[var(--color-bonvoy-ink)]">
            {navItems.map((item) => {
              const active =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "py-2 border-b-2 transition-colors",
                    active
                      ? "border-[var(--color-marriott-red)]"
                      : "border-transparent hover:border-[var(--color-bonvoy-rule)]",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
            <span className="inline-flex items-center gap-1 text-[var(--color-bonvoy-muted)] cursor-default">
              Vacations <ChevronDown size={14} />
            </span>
            <span className="inline-flex items-center gap-1 text-[var(--color-bonvoy-muted)] cursor-default">
              Offers <ChevronDown size={14} />
            </span>
          </nav>

          <div className="ml-auto flex items-center gap-3">
            <button
              aria-label="Search"
              className="p-2 text-[var(--color-bonvoy-ink)] hover:bg-[var(--color-bonvoy-mist)] rounded-full"
            >
              <Search size={18} />
            </button>
            <button
              aria-label="Favorites"
              className="hidden sm:inline-flex p-2 text-[var(--color-bonvoy-ink)] hover:bg-[var(--color-bonvoy-mist)] rounded-full"
            >
              <Heart size={18} />
            </button>

            {guest ? (
              <Link
                href="/profile"
                className="hidden sm:inline-flex items-center gap-1.5 hover:text-white/80"
              >
                Profile
              </Link>
            ) : null}
            {guest ? (
              <Link
                href="/trips"
                className="inline-flex items-center gap-2 rounded-full bg-[var(--color-marriott-red)] text-white px-3.5 py-1.5 text-[13px] font-medium hover:bg-[var(--color-marriott-red-dark)] transition-colors"
              >
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{ background: guest.tier_color }}
                  aria-hidden
                />
                <span className="hidden sm:inline">{guest.name.split(" ")[0]}</span>
                <span className="hidden md:inline text-white/80">
                  · {guest.points.toLocaleString()} pts
                </span>
              </Link>
            ) : (
              <Link
                href="/sign-in"
                className="inline-flex items-center rounded-full border border-[var(--color-bonvoy-ink)] px-3.5 py-1.5 text-[13px] font-medium text-[var(--color-bonvoy-ink)] hover:bg-[var(--color-bonvoy-ink)] hover:text-white transition-colors"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setOpen(false)}
          />
          <div className="absolute left-0 top-0 h-full w-[80%] max-w-[320px] bg-white p-5 shadow-xl">
            <button
              aria-label="Close"
              className="mb-4 p-2 -ml-2"
              onClick={() => setOpen(false)}
            >
              <X size={22} />
            </button>
            <nav className="flex flex-col gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className="py-3 text-[16px] border-b border-[var(--color-bonvoy-rule)]"
                >
                  {item.label}
                </Link>
              ))}
              <Link
                href="/sign-in"
                onClick={() => setOpen(false)}
                className="py-3 text-[16px] border-b border-[var(--color-bonvoy-rule)]"
              >
                {guest ? "Switch persona" : "Sign In or Join"}
              </Link>
            </nav>
          </div>
        </div>
      )}
    </header>
  );
}
