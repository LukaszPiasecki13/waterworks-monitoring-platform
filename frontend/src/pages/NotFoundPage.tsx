import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { AlertCircle } from 'lucide-react';

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-dvh flex-col items-center justify-center bg-neutral-50 px-4">
      <div className="text-center">
        <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-amber-100">
          <AlertCircle className="h-8 w-8 text-amber-600" />
        </div>
        <h1 className="mb-2 text-4xl font-bold text-neutral-900">404</h1>
        <h2 className="mb-4 text-2xl font-semibold text-neutral-900">Strona nie znaleziona</h2>
        <p className="mb-8 max-w-md text-neutral-600">
          Strona, którą szukasz, nie istnieje. Mogło to być spowodowane zmianą adresu lub błędem linkowania.
        </p>
        <Button onClick={() => navigate('/')}>
          Wróć do strony głównej
        </Button>
      </div>
    </div>
  );
}
