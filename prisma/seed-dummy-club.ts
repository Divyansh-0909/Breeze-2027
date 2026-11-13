import { PrismaClient } from "@prisma/client";
import { createClient } from "@supabase/supabase-js";

const prisma = new PrismaClient();

// Use environment variables for Supabase admin client
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!;

const TEST_CLUB_EMAIL = "testclub@breeze2027.com";
const TEST_CLUB_PASSWORD = "TestClub@2027";
const TEST_CLUB_NAME = "TEST CLUB";

async function main() {
  console.log("🏢 Setting up dummy test club...\n");

  // Create Supabase admin client
  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
    auth: { autoRefreshToken: false, persistSession: false },
  });

  // Step 1: Create auth user
  console.log("📧 Creating auth user...");
  let userId: string;

  // Check if user already exists
  const { data: existingUsers } = await supabase.auth.admin.listUsers();
  const existingUser = (existingUsers?.users as any[])?.find(
    (u: any) => u.email === TEST_CLUB_EMAIL
  );

  if (existingUser) {
    userId = existingUser.id;
    console.log(`   User already exists: ${userId}`);
  } else {
    const { data: newUser, error: createError } =
      await supabase.auth.admin.createUser({
        email: TEST_CLUB_EMAIL,
        password: TEST_CLUB_PASSWORD,
        email_confirm: true,
      });

    if (createError) {
      console.error("❌ Failed to create auth user:", createError.message);
      console.log("\n📝 Manual creation required. Use these SQL queries:");
      console.log("   1. Create user in Supabase Dashboard -> Authentication -> Users -> Add User");
      console.log(`   2. Email: ${TEST_CLUB_EMAIL}`);
      console.log(`   3. Password: ${TEST_CLUB_PASSWORD}`);
      console.log("   4. Then run the SQL in prisma/dummy-club-setup.sql");
      process.exit(1);
    }

    userId = newUser.user.id;
    console.log(`   Created user: ${userId}`);
  }

  // Step 2: Create role entry
  console.log("🔑 Creating role entry...");
  const existingRole = await prisma.roles.findFirst({
    where: { email: TEST_CLUB_EMAIL },
  });

  if (existingRole) {
    console.log("   Role already exists");
  } else {
    await prisma.roles.create({
      data: {
        id: userId,
        club_name: TEST_CLUB_NAME,
        email: TEST_CLUB_EMAIL,
      },
    });
    console.log("   Role created");
  }

  // Step 3: Create sample events
  console.log("📅 Creating sample events...");
  const existingEvents = await prisma.eventItem.findMany({
    where: { event_org: TEST_CLUB_NAME },
  });

  let eventIds: string[] = [];

  if (existingEvents.length > 0) {
    console.log(`   ${existingEvents.length} events already exist`);
    eventIds = existingEvents.map((e) => e.id);
  } else {
    const events = await Promise.all([
      prisma.eventItem.create({
        data: {
          event_name: "Rhythm & Blues Night",
          event_description:
            "An evening of soulful music performances featuring talented artists from across the campus.",
          event_price: 150,
          event_type: "Cultural",
          event_venue: "Open Air Theatre",
          event_date: "Feb 15th 2027",
          event_org: TEST_CLUB_NAME,
          image_url:
            "https://via.placeholder.com/400x300?text=Rhythm+Blues",
          registration_open: true,
        },
      }),
      prisma.eventItem.create({
        data: {
          event_name: "Code Sprint 2027",
          event_description:
            "A 6-hour competitive coding challenge for beginners and intermediates. Solo or pair entries allowed.",
          event_price: 200,
          event_type: "Technical",
          event_venue: "Computer Lab A",
          event_date: "Feb 16th 2027",
          event_org: TEST_CLUB_NAME,
          image_url:
            "https://via.placeholder.com/400x300?text=Code+Sprint",
          registration_open: true,
        },
      }),
      prisma.eventItem.create({
        data: {
          event_name: "Art Exhibition",
          event_description:
            "Showcasing student artwork including paintings, digital art, and sculptures.",
          event_price: 50,
          event_type: "Cultural",
          event_venue: "Gallery Hall",
          event_date: "Feb 17th 2027",
          event_org: TEST_CLUB_NAME,
          image_url:
            "https://via.placeholder.com/400x300?text=Art+Exhibition",
          registration_open: false,
        },
      }),
    ]);
    eventIds = events.map((e) => e.id);
    console.log(`   Created ${events.length} events`);
  }

  // Step 4: Create sample approved transactions
  console.log("💰 Creating sample approved transactions...");
  const testTokens = ["TESTCLUB_TX_001", "TESTCLUB_TX_002", "TESTCLUB_TX_003"];

  const existingTx = await prisma.submittedTransaction.findMany({
    where: { token: { in: testTokens } },
  });

  if (existingTx.length > 0) {
    console.log(`   ${existingTx.length} transactions already exist`);
  } else {
    // Create transactions
    await prisma.submittedTransaction.create({
      data: {
        token: "TESTCLUB_TX_001",
        name: "Rahul Sharma",
        email: "rahul@test.com",
        phone: "9876543210",
        address: "R2024001",
        amount: 350,
        cart: {},
        approved: true,
        rejected: false,
        email_sent: true,
        accommodation: [],
        accommodation_price: 0,
        student_details: "B.Tech CSE - 2nd Year",
      },
    });

    await prisma.submittedTransaction.create({
      data: {
        token: "TESTCLUB_TX_002",
        name: "Priya Patel",
        email: "priya@test.com",
        phone: "9876543211",
        address: "R2024002",
        amount: 200,
        cart: {},
        approved: true,
        rejected: false,
        email_sent: true,
        accommodation: [],
        accommodation_price: 0,
        student_details: "B.Tech ECE - 3rd Year",
      },
    });

    await prisma.submittedTransaction.create({
      data: {
        token: "TESTCLUB_TX_003",
        name: "Amit Kumar",
        email: "amit@test.com",
        phone: "9876543212",
        address: "R2024003",
        amount: 150,
        cart: {},
        approved: true,
        rejected: false,
        email_sent: true,
        accommodation: [],
        accommodation_price: 0,
        student_details: "B.Tech IT - 1st Year",
      },
    });

    console.log("   Created 3 test transactions");

    // Link transactions to events
    if (eventIds.length >= 2) {
      await prisma.confirmedEvent.createMany({
        data: [
          { token: "TESTCLUB_TX_001", id: eventIds[0], quantity: 1 }, // Rhythm & Blues
          { token: "TESTCLUB_TX_001", id: eventIds[1], quantity: 1 }, // Code Sprint
          { token: "TESTCLUB_TX_002", id: eventIds[1], quantity: 1 }, // Code Sprint
          { token: "TESTCLUB_TX_003", id: eventIds[0], quantity: 1 }, // Rhythm & Blues
        ],
        skipDuplicates: true,
      });
      console.log("   Linked transactions to events");
    }
  }

  console.log("\n✅ Dummy club setup complete!");
  console.log("─────────────────────────────────");
  console.log(`📧 Email:    ${TEST_CLUB_EMAIL}`);
  console.log(`🔒 Password: ${TEST_CLUB_PASSWORD}`);
  console.log(`🏢 Club:     ${TEST_CLUB_NAME}`);
  console.log(`🌐 Login:    http://localhost:3000/admin/login`);
  console.log(`📊 Dashboard: http://localhost:3000/admin/clubs`);
  console.log("─────────────────────────────────");
}

main()
  .catch((e) => {
    console.error("❌ Error:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
