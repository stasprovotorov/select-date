-- Create table for storing selected calendar dates
CREATE TABLE IF NOT EXISTS public.calendar_dates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, date)
);

-- Enable Row Level Security
ALTER TABLE public.calendar_dates ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for CRUD operations
CREATE POLICY "calendar_dates_select_own"
  ON public.calendar_dates FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "calendar_dates_insert_own"
  ON public.calendar_dates FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "calendar_dates_delete_own"
  ON public.calendar_dates FOR DELETE
  USING (auth.uid() = user_id);

-- Index for better performance on user queries
CREATE INDEX IF NOT EXISTS idx_calendar_dates_user_id ON public.calendar_dates(user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_dates_date ON public.calendar_dates(date);
