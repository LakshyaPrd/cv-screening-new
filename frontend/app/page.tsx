import Link from 'next/link';
import { FileUp, Briefcase, Users, Settings } from 'lucide-react';

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          CV Screening Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Bulk CV & Portfolio OCR, Rule-Based JD Matching & CRM Integration
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/upload"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Upload CVs
          </Link>
          <Link
            href="/job-descriptions"
            className="bg-gray-800 text-white px-8 py-3 rounded-lg font-semibold hover:bg-gray-900 transition"
          >
            View Job Descriptions
          </Link>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <FeatureCard
          icon={<FileUp className="w-8 h-8" />}
          title="Bulk Upload"
          description="Upload hundreds of CVs and portfolios in a single batch for processing"
          href="/upload"
        />
        <FeatureCard
          icon={<Briefcase className="w-8 h-8" />}
          title="Job Descriptions"
          description="Create JDs with requirements and custom scoring weights"
          href="/job-descriptions"
        />
        <FeatureCard
          icon={<Users className="w-8 h-8" />}
          title="Batch Management"
          description="Track processing status and view extracted candidate data"
          href="/batches"
        />
        <FeatureCard
          icon={<Settings className="w-8 h-8" />}
          title="Admin Panel"
          description="Configure skills, tools dictionaries and scoring parameters"
          href="/admin"
        />
      </div>

      <div className="mt-16 bg-white rounded-xl p-8 shadow-sm border border-gray-200">
        <h2 className="text-2xl font-bold mb-4 text-gray-900">How It Works</h2>
        <ol className="space-y-4">
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
              1
            </span>
            <div>
              <h3 className="font-semibold text-gray-900">Upload CVs</h3>
              <p className="text-gray-600">
                Bulk upload PDF or image files. OCR extracts text using Tesseract.
              </p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
              2
            </span>
            <div>
              <h3 className="font-semibold text-gray-900">Create Job Description</h3>
              <p className="text-gray-600">
                Define must-have skills, tools, and role keywords with custom weights.
              </p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
              3
            </span>
            <div>
              <h3 className="font-semibold text-gray-900">Match Candidates</h3>
              <p className="text-gray-600">
                Rule-based matching generates explainable scores (0-100) for each candidate.
              </p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
              4
            </span>
            <div>
              <h3 className="font-semibold text-gray-900">Review & Shortlist</h3>
              <p className="text-gray-600">
                Filter, rank, and shortlist candidates with detailed justifications.
              </p>
            </div>
          </li>
        </ol>
      </div>

      <div className="mt-8 grid md:grid-cols-3 gap-6">
        <InfoCard
          title="✅ No AI/ML"
          description="100% rule-based matching - predictable and auditable"
        />
        <InfoCard
          title="✅ No Recurring Costs"
          description="Open-source OCR (Tesseract) - no per-document fees"
        />
        <InfoCard
          title="✅ Explainable Results"
          description="Detailed score breakdowns with plain-English justifications"
        />
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  href,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition group"
    >
      <div className="text-blue-600 mb-4 group-hover:scale-110 transition">
        {icon}
      </div>
      <h3 className="font-semibold text-lg mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </Link>
  );
}

function InfoCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <h3 className="font-semibold text-green-900 mb-1">{title}</h3>
      <p className="text-green-700 text-sm">{description}</p>
    </div>
  );
}
