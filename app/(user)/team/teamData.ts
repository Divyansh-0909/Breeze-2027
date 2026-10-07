export type Person = { name: string; role: string; image: string };
export type Group = { name: string; code: string; people: Person[] };

export const coordinators: Person[] = [
  { name: "Aparna Balakrishnan", role: "Chairperson", image: "/Aparna.jpeg" },
  { name: "Bhavya Besoya", role: "Co-Chairperson", image: "/bhavya.jpeg" },
  { name: "Vedant Dubey", role: "Administrator", image: "/vedant.jpeg" },
  { name: "Jhalak Gupta", role: "Administrator", image: "/jhalak.jpeg" },
];

export const groups: Group[] = [
  { name: "Marketing", code: "MKT", people: [
    { name: "Navya Sharma", role: "Marketing Lead", image: "/Navya_Sharma.jpg" },
    { name: "Sweta Agrahari", role: "Marketing Lead", image: "/Sweta.jpg" },
  ]},
  { name: "Public Relations", code: "PR", people: [
    { name: "Anubhav Kansal", role: "PR Lead", image: "/Anubhav.jpeg" },
    { name: "Nithya Pasupuleti", role: "PR Lead", image: "/Nithya.jpeg" },
  ]},
  { name: "Content", code: "CNT", people: [
    { name: "Kovid Bhardwaj", role: "Content Lead", image: "/Kovid-Bhardwaj.jpg" },
    { name: "Aviral Mishra", role: "Content Lead", image: "/Aviral.jpg" },
  ]},
  { name: "Web Development", code: "WEB", people: [
    { name: "Khushwant Singh", role: "Web Dev Lead", image: "/Khushwant.jpg" },
    { name: "Aditya Govil", role: "Web Dev Lead", image: "/govil.jpg" },
  ]},
  { name: "Sponsorship", code: "SPN", people: [
    { name: "Shriya Agarwal", role: "Sponsorship Lead", image: "/Shriya Agarwal Spons Lead.jpeg" },
    { name: "Saksham Shukla", role: "Sponsorship Lead", image: "/saksham.jpeg" },
    { name: "Yashita", role: "Sponsorship Lead", image: "/yashita.jpg" },
  ]},
  { name: "Videography", code: "VID", people: [
    { name: "Shubh Choubey", role: "Videography Lead", image: "/Shubh.PNG" },
    { name: "Rupin Roshan", role: "Videography Lead", image: "/Rupinroshan.jpg" },
    { name: "Jaideep K", role: "Videography Lead", image: "/Jaideep.JPG" },
  ]},
  { name: "Design", code: "DSN", people: [
    { name: "Shrijita Guha", role: "Design Lead", image: "/Srijita.jpeg" },
    { name: "Shaivi Dhandapani", role: "Design Lead", image: "/shaivi.jpeg" },
    { name: "Tanya Edlyn", role: "UI/UX Design Lead", image: "/tanya.jpeg" },
  ]},
];
