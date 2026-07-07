// details.tsx

export interface TeamMember {
  id: number;
  name: string;
  role: string;
  image: string;
  bio: string;
  year: string; // Using 'year' instead of 'stats' as per previous request
}

const rawData = [
  // MISSING IMAGES - Using placeholders or keeping broken path if user intends to upload
  { key: 1, img: "/Aparna.jpeg", title: "Chairperson", name: "Aparna Balakrishnan", year: "2027" }, 
  { key: 2, img: "/bhavya.jpeg", title: "Co-Chairperson", name: "Bhavya Besoya", year: "2027" },
  { key: 3, img: "/vedant.jpeg", title: "Administrator", name: "Vedant Dubey", year: "2027" },
  { key: 4, img: "/jhalak.jpeg", title: "Administrator", name: "Jhalak Gupta", year: "2027" },
  { key: 5, img: "/saksham.jpeg", title: "Advisor", name: "Saksham Shukla", year: "2026" },
  
  // VERIFIED EXISTING IMAGES
  { key: 6, img: "/Navya_Sharma.jpg", title: "Marketing Lead", name: "Navya Sharma", year: "2028" },
  { key: 7, img: "/Sweta.jpg", title: "Marketing Lead", name: "Sweta Agrahari", year: "2027" },
  
  // UNSUPPORTED FORMATS (Browser won't render DNG/HEIC/HEIF)
  { key: 8, img: "/Anubhav.jpeg", title: "Public Relations Lead", name: "Anubhav Kansal", year: "2028" },
  { key: 9, img: "/Nithya.jpeg", title: "Public Relations Lead", name: "Nithya Pasupuleti", year: "2028" },
  
  { key: 10, img: "/Shubh.PNG", title: "Videography Lead", name: "Shubh Choubey", year: "2028" },
  { key: 11, img: "/Rupinroshan.jpg", title: "Videography Lead", name: "Rupin Roshan", year: "2027" },
  { key: 12, img: "/Srijita.jpeg", title: "Design Lead", name: "Shrijita Guha", year: "2028" },
  { key: 13, img: "/shaivi.jpeg", title: "Design Lead", name: "Shaivi Dhandapani", year: "2028" },
  { key: 14, img: "/tanya.jpeg", title: "UI/UX Design Lead", name: "Tanya Edlyn", year: "2026" },
  { key: 15, img: "/Kovid-Bhardwaj.jpg", title: "Content Lead", name: "Kovind Bhardwaj", year: "2027" },
  { key: 16, img: "/Aviral.jpg", title: "Content Lead", name: "Aviral Mishra", year: "2027" },
  { key: 17, img: "/vidhushi.jpg", title: "Decor Lead", name: "Vidhushi Prateek", year: "2028" },
  { key: 18, img: "/jahnavi.jpeg", title: "Decor Lead", name: "Jahnavi Verma", year: "2028" },
  { key: 19, img: "/Khushwant.jpg", title: "Web Development Lead", name: "Khushwant Singh", year: "2027" },
  { key: 20, img: "/govil.jpg", title: "Web Development Lead", name: "Aditya Govil", year: "2028" },
  { key: 21, img: "/Angel.PNG", title: "Food Lead", name: "Angel Yunas", year: "2028" },
  { key: 22, img: "/AdhityaSuresh_Food.jpg", title: "Food Lead", name: "Adhitya Suresh", year: "2026" },
  { key: 23, img: "/ArshBhasin.jpg", title: "Event Management Lead", name: "Arsh Bhasin", year: "2027" },
  { key: 24, img: "/yashika.jpg", title: "Event Management Lead", name: "Yashika Gupta", year: "2027" },
  { key: 25, img: "/Arnav_Aggarwal.jpg", title: "Event Management Lead", name: "Arnav Aggarwal", year: "2027" },
  { key: 26, img: "/Jaideep.JPG", title: "Production Lead", name: "Jaideep K", year: "2026" },
  { key: 27, img: "/kushagr.jpeg", title: "Informal Games Lead", name: "Kushagr Saigal", year: "2028" },
  { key: 28, img: "/shivank.jpeg", title: "Informal Games Lead", name: "Shivaank Garg", year: "2028" },
  { key: 29, img: "/Ayushi.jpg", title: "Transportation Lead", name: "Ayushi", year: "2028" },
  { key: 30, img: "/yatharth.jpeg", title: "Security Lead", name: "Yatharth Mittal", year: "2027" },
  { key: 31, img: "/Tabitha.jpg", title: "Security Lead", name: "Tabitha Williems", year: "2028" },
  { key: 32, img: "/TANISHKA.jpeg", title: "Hospitality Lead", name: "Tanishka Jain", year: "2027" },
  { key: 33, img: "/vignesh.jpeg", title: "Hospitality Lead", name: "Vignesh A", year: "2028" },
  { key: 34, img: "/Rahul.jpeg", title: "Accommodation Lead", name: "Rahul Rathnavel", year: "2028" },
  { key: 35, img: "/Shanmukh.jpg", title: "Accommodation Lead", name: "Shanmukha S. Kola", year: "2028" },
  { key: 36, img: "/Reva.jpg", title: "Security Lead", name: "Reva Sonawane", year: "2027" },
];

export const teamMembers: TeamMember[] = rawData.map((item) => ({
  id: item.key,
  name: item.name,
  role: item.title,
  image: item.img,
  year: item.year,
  bio: `The ${item.title} stands as a pillar in the larger vision.
Thirty-six leaders, each owning their domain.
Precision in planning. Passion in execution.
Every department moving in sync.
Because Breeze SNU is Neon Nirvana — and we make it happen.`,
}));