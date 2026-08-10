import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Lock } from 'lucide-react';

export function ForbiddenPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-dvh flex-col items-center justify-center bg-neutral-50 px-4">
      <div className="text-center">
        <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
          <Lock className="h-8 w-8 text-red-600" />
        </div>
        <h1 className="mb-2 text-4xl font-bold text-neutral-900">403</h1>
        <h2 className="mb-4 text-2xl font-semibold text-neutral-900">Dostęp zabroniony</h2>
        <p className="mb-8 max-w-md text-neutral-600">
          Nie masz uprawnień do dostępu do tej strony. Jeśli uważasz, że to błąd, skontaktuj się z administratorem.
        </p>
        <Button onClick={() => navigate('/')}>
          Wróć do strony głównej
        </Button>
      </div>
    </div>
  );
}
