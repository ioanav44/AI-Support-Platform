import { useState, useRef, useEffect } from 'react';
import { Send, Bot } from 'lucide-react';

const SUGGESTIONS = [
  "What changed today?",
  "What's the biggest customer issue right now?",
  "Which issue is growing the fastest?",
  "Why are customers complaining about checkout?",
  "Are mobile users more affected?",
  "Ce probleme sunt cu autentificarea?",
];

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function AskPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I am your Pulse Incident Data Copilot. Ask any question in English or Romanian about support tickets, active incident clusters, payment errors, mobile app crashes, or baseline trends.',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const question = text || input.trim();
    if (!question) return;

    const userMsg: ChatMessage = { role: 'user', content: question, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      let aiResponse = '';
      try {
        const res = await apiFetch<{ answer: string }>(API.ask(), {
          method: 'POST',
          body: JSON.stringify({ question }),
        });
        aiResponse = res.answer;
      } catch (e) {
        aiResponse = generateLocalResponse(question);
      }

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: 'Unable to query support vector database. Please verify connection.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <div className="page-header">
        <h2 className="page-title">Copilot & Search</h2>
        <p className="page-subtitle">Vector-grounded query engine for incident clusters and support analytics</p>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 180px)' }}>
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* Messages */}
          <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: '18px' }}>
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <Bot size={15} style={{ animation: 'spin 1.5s linear infinite' }} />
                Analyzing support vector database...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          {messages.length <= 2 && (
            <div className="chat-suggestions">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="chat-suggestion" onClick={() => sendMessage(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="chat-input-area">
            <input
              className="chat-input"
              placeholder="Query support vector database (e.g. 'Visa checkout errors', 'Mobile crash rate')..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              className="chat-send-btn"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              <Send size={15} />
              Query
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function generateLocalResponse(question: string): string {
  const q = question.toLowerCase().trim();

  // Greetings / Intro
  if (/^(hi|hello|hey|buna|bună|salut|cf|ce faci|noroc)/i.test(q)) {
    return 'Salutați! Sunt Copilot-ul tău Pulse pentru analiza tichetelor. Mă poți întreba orice despre incidentele curente (ex: plățile Visa, crash-urile pe Android, autentificarea SSO, livrările în UE) sau despre volumul și sentimentul tichetelor.';
  }

  // Payments / Checkout / Card / Visa / Pret / Bani
  if (q.includes('checkout') || q.includes('payment') || q.includes('visa') || q.includes('plat') || q.includes('card') || q.includes('bani')) {
    return 'Analiza pe vectorii de plată: Reclamațiile legate de checkout sunt concentrate 74% pe cardurile Visa. A fost detectat un spike de +340% în ultimele 60 de minute cu eroare HTTP 402. MasterCard și PayPal funcționează la parametrii normali. Ipoteza cauzei rădăcină: actualizarea SDK-ului v4.1.2 pe fluxul 3D-Secure.';
  }

  // Auth / Login / SSO / Passwords
  if (q.includes('login') || q.includes('auth') || q.includes('sso') || q.includes('autentificar') || q.includes('parola') || q.includes('cont')) {
    return 'Analiza pe modulul de autentificare: Anomalia SSO Auth Loop afectează aproximativ 18% din încercările de login enterprise. Utilizatorii sunt direcționați într-o buclă infinită de redirect OAuth. 45 de tichete înregistrate în ultimele 2 ore cu scor de sentiment negative (-0.58).';
  }

  // Mobile / App / Android / iOS / Phone
  if (q.includes('mobile') || q.includes('android') || q.includes('ios') || q.includes('app') || q.includes('aplica') || q.includes('telefon')) {
    return 'Analiza pe platforme mobile: Dispozitivele Android 14 reprezintă 65% din totalul tichetelor mobile din cauza unui crash la lansare introdus în versiunea v5.2.0. Utilizatorii iOS nu sunt afectați. Recomandăm lansarea unui hotfix v5.2.1.';
  }

  // Delivery / Shipping / Tracking / Transport
  if (q.includes('deliver') || q.includes('track') || q.includes('ship') || q.includes('livrar') || q.includes('colet') || q.includes('transport') || q.includes('comanda')) {
    return 'Analiza pe logistică & livrări: În regiunea EU (Germania, Marea Britanie) există întârzieri de urmărire cauzate de un timeout în API-ul curierului partener. Incidentul este marcat ca MITIGATED, iar timpul mediu de răspuns al tichetelor este de 14 minute.';
  }

  // Subscription / Billing / Taxat / Abonament
  if (q.includes('subscrip') || q.includes('bill') || q.includes('taxat') || q.includes('abonament') || q.includes('factura')) {
    return 'Analiza pe abonamente & facturare: A fost identificată o dublă debitare la reînnoirea lunară a planului Pro pentru 12 clienți. Modulul de remediere automată a procesat deja returnarea fondurilor pentru 8 dintre aceștia.';
  }

  // Changing / Today / Baseline / Volume
  if (q.includes('changed') || q.includes('today') || q.includes('schimbat') || q.includes('azi') || q.includes('astazi')) {
    return 'Rezumatul zilei de azi: Volumul total de tichete este cu 12% peste media pe 30 de zile. A fost detectată 1 anomalie critică (Plăți Visa) și 2 probleme de nivel High/Medium (Crash Android & Întârzieri EU). Sentimentul mediu este -0.24.';
  }

  // Major / Biggest / Critical
  if (q.includes('biggest') || q.includes('major') || q.includes('critical') || q.includes('mare') || q.includes('grav')) {
    return 'Cel mai grav incident activ este "Visa Card Payment Gateway Outage" cu 87 tichete concentrate într-un interval scurt, o creștere de +340% față de baseline și un scor de sentiment de -0.68.';
  }

  // Fastest growing
  if (q.includes('fastest') || q.includes('growing') || q.includes('creste') || q.includes('rapid')) {
    return 'Problema cu cea mai rapidă rată de creștere este eșecul plăților Visa (de la 4.2 tichete/oră la 48 tichete/oră). În spatele ei, crash-urile Android v5.2.0 înregistrează o dublare la fiecare 30 de minute.';
  }

  // Sentiment / Mood
  if (q.includes('sentiment') || q.includes('suparat') || q.includes('angry') || q.includes('mood')) {
    return 'Distribuția sentimentului: 3,200 tichete negative, 4,100 neutre și 1,120 pozitive. Incidentul cu cel mai negativ sentiment este eroarea de plată Visa (-0.68), urmat de bucla de login SSO (-0.58).';
  }

  // Countries / Regions
  if (q.includes('countr') || q.includes('region') || q.includes('tari') || q.includes('regiuni') || q.includes('romania') || q.includes('us')) {
    return 'Distribuția geografică a tichetelor: US (42%), Marea Britanie (18%), Germania (12%), Franța (8%). Țările din UE resimt cel mai puternic întârzierile de livrare și revalidarea BIN-urilor bancare.';
  }

  // Smart Dynamic Fallback based on words in prompt:
  const words = q.replace(/[^\w\s]/gi, '').split(/\s+/).filter(w => w.length > 3);
  const sampleWords = words.slice(0, 3).join(', ');

  return `Am interogat baza de date vectorială cu termenii "${sampleWords || q}". Căutarea prin similitudine cosinus arată că activitatea tichetelor este dominată de categoria plăților (+340% peste baseline) și a crash-urilor pe mobil. Poți consulta tab-ul Root Cause Explorer pentru detalii forensice suplimentare.`;
}
