import { CheckoutForm } from "@/components/checkout/CheckoutForm";

export default function PaymentPreview() {
  return <div className="pt-20"><CheckoutForm token="preview" amount="800" reference="BZ27ABCDEFGHJK" prepared={false} payeeName="Sample recipient" upiId="demo@invalid" preview /></div>;
}
