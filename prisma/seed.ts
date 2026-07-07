import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  console.log("🌱 Seeding database with test data...");

  // Create test cultural events
  const culturalEvent1 = await prisma.eventItem.create({
    data: {
      event_name: "Test Dance Competition",
      event_description: "Test event - Show your moves in this epic dance competition!",
      event_price: 100,
      event_type: "Cultural",
      event_venue: "Test Main Auditorium",
      event_date: "2025-02-15",
      event_org: "BREEZE",
      image_url: "https://via.placeholder.com/400x300?text=Test+Dance",
    },
  });

  const culturalEvent2 = await prisma.eventItem.create({
    data: {
      event_name: "Test Music Festival",
      event_description: "Test event - Live performances from test bands!",
      event_price: 150,
      event_type: "Cultural",
      event_venue: "Test Open Air Theatre",
      event_date: "2025-02-16",
      event_org: "BREEZE",
      image_url: "https://via.placeholder.com/400x300?text=Test+Music",
    },
  });

  const culturalEvent3 = await prisma.eventItem.create({
    data: {
      event_name: "Test Drama Performance",
      event_description: "Test event - Watch amazing theatrical performances!",
      event_price: 120,
      event_type: "Cultural",
      event_venue: "Test Auditorium Hall",
      event_date: "2025-02-17",
      event_org: "BREEZE",
      image_url: "https://via.placeholder.com/400x300?text=Test+Drama",
    },
  });

  // Create test technical events
  const technicalEvent1 = await prisma.eventItem.create({
    data: {
      event_name: "Test Hackathon 2025",
      event_description: "Test event - 24-hour coding challenge with amazing test prizes!",
      event_price: 200,
      event_type: "Technical",
      event_venue: "Test Computer Lab",
      event_date: "2025-02-18",
      event_org: "BREEZE",
      image_url: "https://via.placeholder.com/400x300?text=Test+Hackathon",
    },
  });

  const technicalEvent2 = await prisma.eventItem.create({
    data: {
      event_name: "Test Robotics Competition",
      event_description: "Test event - Build and battle with your test robots!",
      event_price: 250,
      event_type: "Technical",
      event_venue: "Test Engineering Block",
      event_date: "2025-02-19",
      event_org: "BREEZE",
      image_url: "https://via.placeholder.com/400x300?text=Test+Robotics",
    },
  });

  const technicalEvent3 = await prisma.eventItem.create({
    data: {
      event_name: "Test AI Workshop",
      event_description: "Test event - Learn about artificial intelligence and machine learning!",
      event_price: 180,
      event_type: "Technical",
      event_venue: "Test Innovation Lab",
      event_date: "2025-02-20",
      event_org: "BREEZE",
      image_url: "https://via.placeholder.com/400x300?text=Test+AI",
    },
  });

  // Create test merchandise
  const merch1 = await prisma.merchItem.create({
    data: {
      product_name: "Test Breeze T-Shirt",
      product_description: "Test merchandise - Official Breeze 2026 T-shirt for testing",
      product_price: 400,
      image_url: "https://via.placeholder.com/400x400?text=Test+T-Shirt",
    },
  });

  const merch2 = await prisma.merchItem.create({
    data: {
      product_name: "Test Breeze Hoodie",
      product_description: "Test merchandise - Cozy hoodie with test Breeze logo",
      product_price: 800,
      image_url: "https://via.placeholder.com/400x400?text=Test+Hoodie",
    },
  });

  const merch3 = await prisma.merchItem.create({
    data: {
      product_name: "Test Breeze Cap",
      product_description: "Test merchandise - Stylish cap for test purposes",
      product_price: 250,
      image_url: "https://via.placeholder.com/400x400?text=Test+Cap",
    },
  });

  const merch4 = await prisma.merchItem.create({
    data: {
      product_name: "Test Breeze Backpack",
      product_description: "Test merchandise - Durable backpack for testing",
      product_price: 1200,
      image_url: "https://via.placeholder.com/400x400?text=Test+Backpack",
    },
  });

  console.log("✅ Database seeded successfully with test data!");
  console.log(`Created ${3} test cultural events`);
  console.log(`Created ${3} test technical events`);
  console.log(`Created ${4} test merch items`);
  console.log("\n⚠️  All items are prefixed with 'Test' for easy identification");
}

main()
  .catch((e) => {
    console.error("❌ Error seeding database:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
