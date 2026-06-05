type VideoVibersLogoProps = {
  className?: string;
  size?: number;
};

export default function VideoVibersLogo({ className = "", size = 32 }: VideoVibersLogoProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 64"
      width={size}
      height={size}
      className={className}
      role="img"
      aria-labelledby="video-vibers-logo-title"
    >
      <title id="video-vibers-logo-title">Video Vibers logo</title>
      <path
        d="M12 18a8 8 0 0 1 8-8h24a8 8 0 0 1 8 8v25a8 8 0 0 1-8 8H20a8 8 0 0 1-8-8V18Z"
        fill="none"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="4"
      />
      <path d="M52 26l8-5v20l-8-5V26Z" fill="#34d399" stroke="currentColor" strokeLinejoin="round" strokeWidth="3" />
      <path d="M28 24l12 7-12 7V24Z" fill="#fbbf24" />
      <path d="M22 40c5 4 15 4 20 0" fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="3" />
      <path d="M20 25h8m8 0h8" fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="3" />
      <path d="M6 21c-2 3-2 16 0 19M3 26c-1 2-1 7 0 9" fill="none" stroke="#34d399" strokeLinecap="round" strokeWidth="3" />
    </svg>
  );
}
