import { InstagramIcon, LinkedinIcon } from "lucide-react"; // Changed 'Twitter' to 'LinkedinIcon'
import { FaWhatsapp } from "react-icons/fa";

interface SocialLinksProps {
  className?: string;
}

export default function SocialLinks({ className = "" }: SocialLinksProps) {

  return (
    <ul className={`flex space-x-6 text-white ${className}`}>
      {/* Instagram */}
      <li>
        <a
          href="https://www.instagram.com/breeze.snu/?hl=en"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center group"
        >
          <InstagramIcon
            className="w-5 h-5 text-white transition-all duration-300 group-hover:text-red-500 group-hover:drop-shadow-[0_0_8px_rgba(239,68,68,0.8)] group-hover:-translate-y-1 group-hover:scale-110"
          />
        </a>
      </li>

      <li>
        <a
          href="https://linkedin.com/in/breeze2026/" 
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center group"
        >
          <LinkedinIcon
            className="w-5 h-5 text-white transition-all duration-300 group-hover:text-blue-600 group-hover:drop-shadow-[0_0_8px_rgba(37,99,235,0.8)] group-hover:-translate-y-1 group-hover:scale-110"
          />
        </a>
      </li>

      {/* WhatsApp */}
      <li>
        <a
          href="https://wa.me/"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center group"
        >
          <FaWhatsapp
            className="w-5 h-5 text-white transition-all duration-300 group-hover:text-green-400 group-hover:drop-shadow-[0_0_8px_rgba(74,222,128,0.8)] group-hover:-translate-y-1 group-hover:scale-110"
          />
        </a>
      </li>
    </ul>
  );
}