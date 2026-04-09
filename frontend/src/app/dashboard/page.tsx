import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Dashboard from '@/components/Dashboard';
import ParticleBackground from '@/components/ParticleBackground';

export default function DashboardPage() {
  return (
    <div className="min-h-screen flex flex-col mesh-bg selection:bg-primary-container selection:text-on-primary-container">
      <ParticleBackground />
      <Header />
      
      <main className="flex-grow px-6 py-12 relative">
        <Dashboard />
      </main>
      
      <Footer />
    </div>
  );
}
