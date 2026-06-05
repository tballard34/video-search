import { createRootRoute, Link, Outlet, useLocation } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { useEffect, useState } from "react";
import { TbLayoutSidebarLeftCollapse, TbLayoutSidebarLeftExpand, TbRobot, TbSearch, TbVideo } from "react-icons/tb";

import { Providers } from "@/components/providers";
import VideoVibersLogo from "@/components/VideoVibersLogo";

function AppShell() {
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(() => localStorage.getItem("sidebarCollapsed") === "true");

  useEffect(() => {
    localStorage.setItem("sidebarCollapsed", String(isCollapsed));
  }, [isCollapsed]);

  const navItems = [
    { to: "/", label: "Videos", icon: TbVideo, active: location.pathname === "/" || location.pathname.startsWith("/videos") },
    { to: "/search", label: "Search", icon: TbSearch, active: location.pathname === "/search" },
    { to: "/agent", label: "Agent", icon: TbRobot, active: location.pathname === "/agent" },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <aside className={`relative flex flex-col bg-[#0c1220] text-white transition-all duration-300 ${isCollapsed ? "w-16" : "w-16 sm:w-52"}`}>
        <div className={`px-4 py-6 ${isCollapsed ? "flex justify-center" : "flex justify-center sm:items-center sm:gap-3 sm:text-left"}`}>
          <VideoVibersLogo size={isCollapsed ? 28 : 30} className="flex-shrink-0 text-white" />
          {!isCollapsed && <h1 className="hidden text-base font-bold tracking-normal sm:block">Video Vibers</h1>}
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <Link
                key={item.to}
                to={item.to}
                title={isCollapsed ? item.label : ""}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition ${
                  item.active ? "bg-white/10 text-white" : "text-gray-300 hover:bg-white/10 hover:text-white"
                } ${isCollapsed ? "justify-center px-2" : "justify-center px-2 sm:justify-start sm:px-3"}`}
              >
                <Icon size={18} className="flex-shrink-0" />
                {!isCollapsed && <span className="hidden sm:inline">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-white/10 p-3">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-300 transition hover:bg-white/10 hover:text-white ${
              isCollapsed ? "justify-center px-2" : "justify-center px-2 sm:justify-start sm:px-3"
            }`}
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? <TbLayoutSidebarLeftExpand size={18} className="flex-shrink-0" /> : <TbLayoutSidebarLeftCollapse size={18} className="flex-shrink-0" />}
            {!isCollapsed && <span className="hidden sm:inline">Collapse</span>}
          </button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 bg-background">
        <Outlet />
      </main>
    </div>
  );
}

function RootLayout() {
  return (
    <Providers>
      <div className="min-h-screen bg-background">
        <AppShell />
        <TanStackRouterDevtools />
      </div>
    </Providers>
  );
}

export const Route = createRootRoute({
  component: RootLayout,
});
