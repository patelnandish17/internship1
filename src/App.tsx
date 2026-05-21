import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Index from "./pages/Index.tsx";
import NotFound from "./pages/NotFound.tsx";
import Login from "./pages/Login";
import AppLayout from "./components/layout/AppLayout";
import Home from "./pages/Home";
import Companies from "./pages/Companies";
import Categories from "./pages/Categories";
import Compare from "./pages/Compare";
import SkillMapping from "./pages/SkillMapping";
import Analytics from "./pages/Analytics";
import CompanyDetail from "./pages/CompanyDetail";
import HiringRounds from "./pages/HiringRounds";
import Innovox from "./pages/Innovox";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<Login />} />
          <Route element={<AppLayout />}>
            <Route path="/home" element={<Home />} />
            <Route path="/companies" element={<Companies />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/skill-mapping" element={<SkillMapping />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/company/:id" element={<CompanyDetail />} />
            <Route path="/hiring-rounds" element={<HiringRounds />} />
            <Route path="/innovox" element={<Innovox />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
