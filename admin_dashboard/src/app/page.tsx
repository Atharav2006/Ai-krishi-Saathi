import { redirect } from 'next/navigation';

export default function Home() {
    // Redirect root to dashboard (which handles its own auth redirect if needed)
    redirect('/admin?model=price_forecast');
}
