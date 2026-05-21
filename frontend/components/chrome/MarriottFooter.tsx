import Link from "next/link";

const columns: Array<{ heading: string; links: string[] }> = [
  {
    heading: "Find & Reserve",
    links: [
      "Hotels & Resorts",
      "Vacations by Marriott Bonvoy",
      "Homes & Villas",
      "All-Inclusive Resorts",
      "Deals & Packages",
    ],
  },
  {
    heading: "Marriott Bonvoy",
    links: [
      "Overview",
      "Member Benefits",
      "Earn Points",
      "Redeem Points",
      "Credit Cards",
    ],
  },
  {
    heading: "About Marriott",
    links: ["Our Brands", "Careers", "Investor Relations", "Newsroom", "Press Center"],
  },
  {
    heading: "Help",
    links: ["Customer Care", "Site Map", "Privacy Center", "Cookie Preferences", "Terms"],
  },
];

export function MarriottFooter(): React.ReactElement {
  return (
    <footer className="bg-[var(--color-bonvoy-ink)] text-white mt-20">
      <div className="mx-auto max-w-[1280px] px-6 py-14">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10 text-[13px]">
          {columns.map((col) => (
            <div key={col.heading}>
              <h4 className="text-[12px] uppercase tracking-[0.18em] text-white/70 mb-4">
                {col.heading}
              </h4>
              <ul className="space-y-2.5">
                {col.links.map((link) => (
                  <li key={link}>
                    <span className="text-white/85 hover:text-white cursor-default">
                      {link}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 pt-8 border-t border-white/15 flex flex-col md:flex-row md:items-center justify-between gap-4 text-[12px] text-white/60">
          <div className="flex items-center gap-3">
            <span className="font-serif text-[16px] tracking-[0.18em] text-white">
              MARRIOTT
            </span>
            <span className="text-white/40">·</span>
            <span>© 2026 Marriott International, Inc. All rights reserved.</span>
          </div>
          <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
            <span>Tracking Preferences</span>
            <span>Do Not Sell My Personal Information</span>
            <Link href="/sign-in" className="text-white/80 hover:text-white">
              Demo: switch persona
            </Link>
          </div>
        </div>

        <p className="mt-6 text-[11px] leading-relaxed text-white/45 max-w-3xl">
          This is a non-commercial Codefest demo. All data is mocked. Eco
          ratings, arrival briefs, and partner maps are additive prototypes
          built on top of the public Marriott Bonvoy experience and do not
          represent live Marriott data.
        </p>
      </div>
    </footer>
  );
}
