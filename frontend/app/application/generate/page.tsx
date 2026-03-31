"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { generateApplication } from '@/lib/api'

export default function ApplicationGenerationPage() {
  const [internshipData, setInternshipData] = useState<any>(null)
  const [generatedData, setGeneratedData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [hasStartedGeneration, setHasStartedGeneration] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSending, setIsSending] = useState(false)
  
  const router = useRouter()

  useEffect(() => {
    const userId = localStorage.getItem("user_id")
    if (!userId) {
      router.replace('/login')
      return
    }

    const storedData = localStorage.getItem("selected_internship")
    if (!storedData) {
      router.replace('/dashboard')
      return
    }

    const parsedData = JSON.parse(storedData)
    setInternshipData(parsedData)
    
  }, [router])

  const runGeneration = async (data: any) => {
    try {
      const result = await generateApplication(
        data.resume_id,
        data.internship,
        data.match_score,
        data.reasoning
      )
      setGeneratedData(result)
    } catch (err: any) {
      setError(err.message || "Failed to generate application materials")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  }

  const handleSendEmail = async (subject: string, body: string, company: string) => {
    setIsSending(true);
    try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/email/send", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                recipientEmail: `hiring@${company.toLowerCase().replace(/\s/g, '')}.com`, 
                subject: subject,
                body: body
            })
        });
        if (!response.ok) throw new Error("Failed to send email");
        alert("Email processed successfully (check backend logs for SMTP details)!");
    } catch(err: any) {
        alert("Error sending email: " + err.message);
    } finally {
      setIsSending(false);
    }
  }

  const handleDownloadPDF = async (markdown: string, company: string) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/pdf/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          markdown_text: markdown,
          filename: `Resume_${company.replace(/\s/g, '_')}.pdf`
        })
      });
      
      if (!response.ok) throw new Error("Failed to generate PDF");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Resume_${company.replace(/\s/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert("Error downloading PDF: " + err.message);
    }
  }

  if (!internshipData) return null; // Loading initial state

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 font-sans p-6 md:p-12">
      <div className="max-w-5xl mx-auto w-full space-y-8">
        <Link href="/dashboard" className="inline-flex items-center text-blue-600 font-semibold hover:text-blue-800 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="m15 18-6-6 6-6"/></svg>
          Back to Internship Discoveries
        </Link>
        
        <div className="bg-slate-900 rounded-xl p-8 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight mb-2">Application Package</h1>
              <p className="text-slate-300 font-medium text-lg">
                 {internshipData.internship.role} at <span className="text-white font-bold">{internshipData.internship.company}</span>
              </p>
            </div>
            <div className="bg-black/30 px-6 py-3 rounded-lg border border-white/10 mt-4 md:mt-0 text-center">
                <span className="text-4xl font-extrabold text-white">{internshipData.match_score}<span className="text-xl opacity-70">/10</span></span>
                <span className="block text-xs font-bold uppercase tracking-wider text-slate-300 mt-1">Match Score</span>
            </div>
        </div>

        {!hasStartedGeneration && !generatedData && !error && (
            <div className="bg-white border text-center border-slate-200 rounded-xl p-8 shadow-sm">
                <h2 className="text-2xl font-bold mb-4">Ready to Apply?</h2>
                <p className="text-slate-600 mb-6 max-w-2xl mx-auto">
                    We've opened a search for <strong>{internshipData.internship.company}</strong> internships in a new tab. Once you find the perfect role available, click below to generate your tailored application materials.
                </p>
                <Button 
                    onClick={() => {
                        setHasStartedGeneration(true)
                        setIsLoading(true)
                        setError(null)
                        runGeneration(internshipData)
                    }}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg px-8 py-4 h-auto"
                >
                    Generate Application Materials
                </Button>
            </div>
        )}

        {isLoading && (
          <div className="min-h-[400px] flex flex-col items-center justify-center border-2 border-dashed border-slate-200 rounded-2xl bg-white shadow-sm p-8 text-center">
             <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-6"></div>
             <h3 className="text-2xl font-bold text-slate-800 mb-3">Crafting Your Application...</h3>
             <ul className="text-slate-500 font-medium space-y-2 text-left bg-slate-50 px-8 py-4 rounded-xl border border-slate-100">
                <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div> Extracting company context via RAG</li>
                <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse delay-75"></div> Tailoring your resume markdown</li>
                <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse delay-150"></div> Generating persuasive cover letter</li>
                <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse delay-300"></div> Drafting outreach email</li>
             </ul>
          </div>
        )}

        {error && (
            <div className="bg-red-50 text-red-700 p-6 rounded-xl border border-red-200 font-semibold shadow-sm text-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mx-auto mb-3"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                {error}
                <br/>
                <Button onClick={() => window.location.reload()} className="mt-4 bg-red-600 hover:bg-red-700 text-white">Retry Generation</Button>
            </div>
        )}

        {generatedData && !isLoading && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
                
                {/* Tailored Resume preview */}
                <div className="border border-slate-200 bg-white rounded-xl overflow-hidden shadow-md">
                   <div className="flex justify-between items-center bg-slate-100 border-b border-slate-200 px-6 py-4">
                      <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                         <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
                         1. Tailored Resume (Markdown)
                      </h3>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => handleDownloadPDF(generatedData.tailored_resume, internshipData.internship.company)} className="bg-white hover:bg-blue-50 text-blue-700 font-bold border-blue-200">Download as PDF</Button>
                        <Button variant="outline" size="sm" onClick={() => handleCopy(generatedData.tailored_resume)} className="bg-white hover:bg-slate-50 text-slate-700 font-bold border-slate-300">Copy Markdown</Button>
                      </div>
                   </div>
                   <div className="text-sm font-mono max-h-96 overflow-y-auto whitespace-pre-wrap text-slate-700 p-6 leading-relaxed bg-slate-50/50">
                     {generatedData.tailored_resume || "Resume tailoring failed or not provided."}
                   </div>
                </div>

                {/* Cover Letter */}
                <div className="border border-blue-200 bg-white rounded-xl overflow-hidden shadow-md ring-1 ring-blue-50">
                   <div className="flex justify-between items-center border-b border-blue-100 bg-blue-50 px-6 py-4">
                      <h3 className="text-lg font-bold text-blue-900 flex items-center gap-2">
                         <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                         2. Targeted Cover Letter
                      </h3>
                      <Button variant="outline" size="sm" onClick={() => handleCopy(generatedData.cover_letter)} className="bg-white text-blue-700 font-bold border-blue-200 hover:bg-blue-100">Copy Letter</Button>
                   </div>
                   <div className="text-base font-serif whitespace-pre-wrap text-slate-800 p-8 leading-relaxed">
                     {generatedData.cover_letter}
                   </div>
                </div>

                {/* Email Draft */}
                <div className="border border-amber-200 bg-white rounded-xl overflow-hidden shadow-xl ring-2 ring-amber-100/50">
                   <div className="flex justify-between items-center border-b border-amber-200 bg-amber-50 px-6 py-4">
                      <h3 className="text-lg font-bold text-amber-900 flex items-center gap-2">
                         <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-amber-600"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                         3. Outreach Email Draft
                      </h3>
                      <Button variant="outline" size="sm" onClick={() => handleCopy(`Subject: ${generatedData.email_subject}\n\n${generatedData.email_body}`)} className="bg-white text-amber-900 font-bold border-amber-300 hover:bg-amber-100">Copy Email</Button>
                   </div>
                   <div className="text-base text-slate-800 space-y-5 p-8 leading-relaxed">
                      <p className="font-semibold bg-amber-50/70 p-4 rounded-md border border-amber-100/80 text-amber-900 flex items-center">
                         <span className="opacity-60 mr-3 text-xs uppercase tracking-widest font-bold">Subject:</span> 
                         {generatedData.email_subject || ""}
                      </p>
                      <p className="whitespace-pre-wrap px-2 text-lg">{generatedData.email_body || "Email body generation failed."}</p>
                   </div>
                   
                   <div className="bg-amber-50/50 px-6 py-5 border-t border-amber-100 flex justify-between items-center">
                      <p className="text-sm text-amber-700 font-semibold flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-amber-500"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                        Ready to send directly to hiring committee.
                      </p>
                      <Button 
                        onClick={() => handleSendEmail(generatedData.email_subject, generatedData.email_body, internshipData.internship.company)}
                        disabled={isSending}
                        className="bg-amber-600 hover:bg-amber-700 text-white font-bold text-md shadow-lg transition-all hover:-translate-y-0.5 shadow-amber-600/30 px-8 py-6 rounded-full"
                      >
                          {isSending ? "Sending to Queue..." : "Send Application Email Now"}
                      </Button>
                   </div>
                </div>
            </div>
        )}
      </div>
    </div>
  )
}
