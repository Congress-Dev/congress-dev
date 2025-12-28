-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "appropriations";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "prompts";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "sensitive";

-- CreateEnum
CREATE TYPE "legislationchamber" AS ENUM ('House', 'Senate');

-- CreateEnum
CREATE TYPE "legislationtype" AS ENUM ('Bill', 'CRes', 'Res', 'JRes');

-- CreateEnum
CREATE TYPE "legislationversionenum" AS ENUM ('IS', 'IH', 'RAS', 'RAH', 'RFS', 'RFH', 'RDS', 'RHS', 'RCS', 'RCH', 'RS', 'RH', 'PCS', 'PCH', 'CPS', 'CPH', 'EAS', 'EAH', 'ES', 'EH', 'ENR');

-- CreateEnum
CREATE TYPE "legislatorjob" AS ENUM ('Senator', 'Representative');

-- CreateEnum
CREATE TYPE "legislatorvotetype" AS ENUM ('yay', 'nay', 'present', 'abstain');

-- CreateTable
CREATE TABLE "appropriations"."appropriation" (
    "appropriation_id" SERIAL NOT NULL,
    "parent_id" INTEGER,
    "legislation_version_id" INTEGER,
    "legislation_content_id" INTEGER,
    "content_str_indicies" INTEGER[],
    "amount" BIGINT,
    "new_spending" BOOLEAN NOT NULL,
    "fiscal_years" INTEGER[],
    "until_expended" BOOLEAN NOT NULL,
    "expiration_year" INTEGER,
    "target" VARCHAR,
    "purpose" VARCHAR,
    "prompt_batch_id" INTEGER,

    CONSTRAINT "appropriation_pkey" PRIMARY KEY ("appropriation_id")
);

-- CreateTable
CREATE TABLE "prompts"."prompt" (
    "prompt_id" SERIAL NOT NULL,
    "version" VARCHAR NOT NULL,
    "title" VARCHAR NOT NULL,
    "description" VARCHAR,
    "prompt" VARCHAR NOT NULL,
    "model" VARCHAR NOT NULL,

    CONSTRAINT "prompt_pkey" PRIMARY KEY ("prompt_id")
);

-- CreateTable
CREATE TABLE "prompts"."prompt_batch" (
    "prompt_batch_id" SERIAL NOT NULL,
    "prompt_id" INTEGER,
    "legislation_version_id" INTEGER,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(6),
    "attempted" INTEGER NOT NULL,
    "successful" INTEGER NOT NULL,
    "failed" INTEGER NOT NULL,
    "skipped" INTEGER NOT NULL,

    CONSTRAINT "prompt_batch_pkey" PRIMARY KEY ("prompt_batch_id")
);

-- CreateTable
CREATE TABLE "alembic_version" (
    "version_num" VARCHAR(32) NOT NULL,

    CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num")
);

-- CreateTable
CREATE TABLE "congress" (
    "congress_id" SERIAL NOT NULL,
    "session_number" INTEGER,
    "start_year" INTEGER,
    "end_year" INTEGER,

    CONSTRAINT "congress_pkey" PRIMARY KEY ("congress_id")
);

-- CreateTable
CREATE TABLE "legislation" (
    "legislation_id" SERIAL NOT NULL,
    "chamber" "legislationchamber",
    "legislation_type" "legislationtype",
    "number" INTEGER,
    "title" VARCHAR,
    "congress_id" INTEGER,
    "version_id" INTEGER,
    "policy_areas" VARCHAR[],
    "legislative_subjects" VARCHAR[],

    CONSTRAINT "legislation_pkey" PRIMARY KEY ("legislation_id")
);

-- CreateTable
CREATE TABLE "legislation_action_parse" (
    "legislation_action_parse_id" SERIAL NOT NULL,
    "legislation_version_id" INTEGER,
    "legislation_content_id" INTEGER,
    "actions" JSONB[],
    "citations" JSONB[],

    CONSTRAINT "legislation_action_parse_pkey" PRIMARY KEY ("legislation_action_parse_id")
);

-- CreateTable
CREATE TABLE "legislation_committee" (
    "legislation_committee_id" SERIAL NOT NULL,
    "system_code" VARCHAR,
    "chamber" "legislationchamber",
    "name" VARCHAR,
    "committee_type" VARCHAR,
    "congress_id" INTEGER,
    "thomas_id" VARCHAR,
    "parent_id" INTEGER,
    "url" VARCHAR,
    "minority_url" VARCHAR,
    "address" VARCHAR,
    "phone" VARCHAR,
    "rss_url" VARCHAR,
    "jurisdiction" VARCHAR,
    "youtube_id" VARCHAR,
    "committee_id" VARCHAR,

    CONSTRAINT "legislation_committee_pkey" PRIMARY KEY ("legislation_committee_id")
);

-- CreateTable
CREATE TABLE "legislation_committee_association" (
    "committee_association_id" SERIAL NOT NULL,
    "legislation_committee_id" INTEGER,
    "referred_date" TIMESTAMP(6),
    "discharge_date" TIMESTAMP(6),
    "legislation_id" INTEGER,
    "congress_id" INTEGER,

    CONSTRAINT "legislation_committee_association_pkey" PRIMARY KEY ("committee_association_id")
);

-- CreateTable
CREATE TABLE "legislation_content" (
    "legislation_content_id" SERIAL NOT NULL,
    "parent_id" INTEGER,
    "lc_ident" VARCHAR,
    "order_number" INTEGER,
    "section_display" VARCHAR,
    "heading" VARCHAR,
    "content_str" VARCHAR,
    "content_type" VARCHAR,
    "legislation_version_id" INTEGER,

    CONSTRAINT "legislation_content_pkey" PRIMARY KEY ("legislation_content_id")
);

-- CreateTable
CREATE TABLE "legislation_content_summary" (
    "legislation_content_summary_id" SERIAL NOT NULL,
    "legislation_content_id" INTEGER,
    "summary" VARCHAR,
    "prompt_batch_id" INTEGER,

    CONSTRAINT "legislation_content_summary_pkey" PRIMARY KEY ("legislation_content_summary_id")
);

-- CreateTable
CREATE TABLE "legislation_content_tag" (
    "legislation_content_tag_id" SERIAL NOT NULL,
    "prompt_batch_id" INTEGER,
    "legislation_content_id" INTEGER,
    "tags" VARCHAR[],

    CONSTRAINT "legislation_content_tag_pkey" PRIMARY KEY ("legislation_content_tag_id")
);

-- CreateTable
CREATE TABLE "legislation_sponsorship" (
    "legislation_sponsorship_id" SERIAL NOT NULL,
    "legislator_bioguide_id" VARCHAR,
    "legislation_id" INTEGER,
    "cosponsor" BOOLEAN,
    "original" BOOLEAN,
    "sponsorship_date" DATE,
    "sponsorship_withdrawn_date" DATE,

    CONSTRAINT "legislation_sponsorship_pkey" PRIMARY KEY ("legislation_sponsorship_id")
);

-- CreateTable
CREATE TABLE "legislation_version" (
    "legislation_version_id" SERIAL NOT NULL,
    "legislation_version" "legislationversionenum",
    "effective_date" DATE,
    "legislation_id" INTEGER,
    "version_id" INTEGER,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(6),

    CONSTRAINT "legislation_version_pkey" PRIMARY KEY ("legislation_version_id")
);

-- CreateTable
CREATE TABLE "legislation_vote" (
    "id" SERIAL NOT NULL,
    "number" INTEGER NOT NULL,
    "legislation_id" INTEGER,
    "question" VARCHAR,
    "independent" JSONB,
    "republican" JSONB,
    "democrat" JSONB,
    "total" JSONB,
    "passed" BOOLEAN,
    "chamber" "legislationchamber",
    "congress_id" INTEGER,
    "datetime" TIMESTAMP(6),

    CONSTRAINT "legislation_vote_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "legislative_policy_area" (
    "legislative_policy_area_id" SERIAL NOT NULL,
    "name" VARCHAR,
    "congress_id" INTEGER,

    CONSTRAINT "legislative_policy_area_pkey" PRIMARY KEY ("legislative_policy_area_id")
);

-- CreateTable
CREATE TABLE "legislative_policy_area_association" (
    "legislative_policy_area_association_id" SERIAL NOT NULL,
    "legislative_policy_area_id" INTEGER,
    "legislation_id" INTEGER,

    CONSTRAINT "legislative_policy_area_association_pkey" PRIMARY KEY ("legislative_policy_area_association_id")
);

-- CreateTable
CREATE TABLE "legislative_subject" (
    "legislative_subject_id" SERIAL NOT NULL,
    "subject" VARCHAR,
    "congress_id" INTEGER,

    CONSTRAINT "legislative_subject_pkey" PRIMARY KEY ("legislative_subject_id")
);

-- CreateTable
CREATE TABLE "legislative_subject_association" (
    "legislative_subject_association_id" SERIAL NOT NULL,
    "legislative_subject_id" INTEGER,
    "legislation_id" INTEGER,

    CONSTRAINT "legislative_subject_association_pkey" PRIMARY KEY ("legislative_subject_association_id")
);

-- CreateTable
CREATE TABLE "legislator" (
    "legislator_id" SERIAL NOT NULL,
    "bioguide_id" VARCHAR,
    "first_name" VARCHAR,
    "middle_name" VARCHAR,
    "last_name" VARCHAR,
    "party" VARCHAR,
    "state" VARCHAR,
    "district" INTEGER,
    "image_url" VARCHAR,
    "image_source" VARCHAR,
    "profile" VARCHAR,
    "lis_id" VARCHAR,
    "job" "legislatorjob",
    "congress_id" INTEGER[],
    "twitter" VARCHAR,
    "facebook" VARCHAR,
    "youtube" VARCHAR,
    "instagram" VARCHAR,

    CONSTRAINT "legislator_pkey" PRIMARY KEY ("legislator_id")
);

-- CreateTable
CREATE TABLE "legislator_vote" (
    "id" SERIAL NOT NULL,
    "legislation_vote_id" INTEGER,
    "legislator_bioguide_id" VARCHAR,
    "vote" "legislatorvotetype",

    CONSTRAINT "legislator_vote_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "usc_act_section" (
    "usc_act_section_id" SERIAL NOT NULL,
    "act_section" VARCHAR,
    "usc_title" VARCHAR,
    "usc_section" VARCHAR,
    "usc_popular_name_id" INTEGER,

    CONSTRAINT "usc_act_section_pkey" PRIMARY KEY ("usc_act_section_id")
);

-- CreateTable
CREATE TABLE "usc_chapter" (
    "usc_chapter_id" SERIAL NOT NULL,
    "short_title" VARCHAR,
    "long_title" VARCHAR,
    "document" VARCHAR,
    "usc_ident" VARCHAR,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "usc_release_id" INTEGER,
    "version_id" INTEGER,

    CONSTRAINT "usc_chapter_pkey" PRIMARY KEY ("usc_chapter_id")
);

-- CreateTable
CREATE TABLE "usc_content" (
    "usc_content_id" SERIAL NOT NULL,
    "parent_id" INTEGER,
    "usc_ident" VARCHAR,
    "usc_guid" VARCHAR,
    "order_number" INTEGER,
    "number" VARCHAR,
    "section_display" VARCHAR,
    "heading" VARCHAR,
    "content_str" VARCHAR,
    "content_type" VARCHAR,
    "usc_section_id" INTEGER,
    "version_id" INTEGER,

    CONSTRAINT "usc_content_pkey" PRIMARY KEY ("usc_content_id")
);

-- CreateTable
CREATE TABLE "usc_content_diff" (
    "usc_content_diff_id" SERIAL NOT NULL,
    "usc_ident" VARCHAR,
    "usc_guid" VARCHAR,
    "order_number" INTEGER,
    "number" VARCHAR,
    "section_display" VARCHAR,
    "heading" VARCHAR,
    "content_str" VARCHAR,
    "content_type" VARCHAR,
    "usc_content_id" INTEGER,
    "usc_section_id" INTEGER,
    "usc_chapter_id" INTEGER,
    "legislation_content_id" INTEGER,
    "version_id" INTEGER,

    CONSTRAINT "usc_content_diff_pkey" PRIMARY KEY ("usc_content_diff_id")
);

-- CreateTable
CREATE TABLE "usc_popular_name" (
    "usc_popular_name_id" SERIAL NOT NULL,
    "name" VARCHAR,
    "public_law_number" VARCHAR,
    "act_date" DATE,
    "act_congress" INTEGER,
    "usc_release_id" INTEGER,

    CONSTRAINT "usc_popular_name_pkey" PRIMARY KEY ("usc_popular_name_id")
);

-- CreateTable
CREATE TABLE "usc_release" (
    "usc_release_id" SERIAL NOT NULL,
    "short_title" VARCHAR,
    "effective_date" DATE,
    "long_title" VARCHAR,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "version_id" INTEGER,

    CONSTRAINT "usc_release_pkey" PRIMARY KEY ("usc_release_id")
);

-- CreateTable
CREATE TABLE "usc_section" (
    "usc_section_id" SERIAL NOT NULL,
    "usc_ident" VARCHAR,
    "usc_guid" VARCHAR,
    "parent_id" INTEGER,
    "number" VARCHAR,
    "section_display" VARCHAR,
    "heading" VARCHAR,
    "content_type" VARCHAR,
    "usc_chapter_id" INTEGER,
    "version_id" INTEGER,

    CONSTRAINT "usc_section_pkey" PRIMARY KEY ("usc_section_id")
);

-- CreateTable
CREATE TABLE "version" (
    "version_id" SERIAL NOT NULL,
    "base_id" INTEGER,

    CONSTRAINT "version_pkey" PRIMARY KEY ("version_id")
);

-- CreateTable
CREATE TABLE "sensitive"."user_ident" (
    "user_id" VARCHAR NOT NULL,
    "user_first_name" VARCHAR NOT NULL,
    "user_last_name" VARCHAR NOT NULL,
    "user_state" VARCHAR,
    "user_image" VARCHAR,
    "user_auth_password" VARCHAR,
    "user_auth_google" VARCHAR,
    "user_auth_expiration" TIMESTAMP(6),
    "user_auth_cookie" VARCHAR,

    CONSTRAINT "user_ident_pkey" PRIMARY KEY ("user_id")
);

-- CreateTable
CREATE TABLE "sensitive"."user_legislation" (
    "user_legislation_id" SERIAL NOT NULL,
    "user_id" VARCHAR,
    "legislation_id" INTEGER,

    CONSTRAINT "user_legislation_pkey" PRIMARY KEY ("user_legislation_id")
);

-- CreateTable
CREATE TABLE "sensitive"."user_legislator" (
    "user_legislator_id" SERIAL NOT NULL,
    "user_id" VARCHAR,
    "bioguide_id" VARCHAR,

    CONSTRAINT "user_legislator_pkey" PRIMARY KEY ("user_legislator_id")
);

-- CreateTable
CREATE TABLE "sensitive"."user_llm_query" (
    "user_llm_query_id" SERIAL NOT NULL,
    "user_id" VARCHAR,
    "legislation_version_id" INTEGER,
    "query" VARCHAR NOT NULL,
    "response" VARCHAR NOT NULL,
    "safe" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "user_llm_query_pkey" PRIMARY KEY ("user_llm_query_id")
);

-- CreateTable
CREATE TABLE "sensitive"."user_usc_content" (
    "user_usc_content_id" SERIAL NOT NULL,
    "user_id" VARCHAR,
    "user_usc_content_folder_id" INTEGER,
    "usc_ident" VARCHAR,

    CONSTRAINT "user_usc_content_pkey" PRIMARY KEY ("user_usc_content_id")
);

-- CreateTable
CREATE TABLE "sensitive"."user_usc_content_folder" (
    "user_usc_content_folder_id" SERIAL NOT NULL,
    "user_id" VARCHAR,
    "name" VARCHAR NOT NULL,

    CONSTRAINT "user_usc_content_folder_pkey" PRIMARY KEY ("user_usc_content_folder_id")
);

-- CreateTable
CREATE TABLE "legislation_action" (
    "legislation_action_id" SERIAL NOT NULL,
    "legislation_id" INTEGER,
    "action_date" DATE,
    "text" VARCHAR,
    "action_type" VARCHAR,
    "action_code" VARCHAR,
    "source_code" VARCHAR,
    "source_name" VARCHAR,
    "raw" JSONB,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "legislation_action_pkey" PRIMARY KEY ("legislation_action_id")
);

-- CreateTable
CREATE TABLE "legislation_version_tag" (
    "legislation_version_tag_id" SERIAL NOT NULL,
    "legislation_version_id" INTEGER,
    "tags" VARCHAR[],
    "prompt_batch_id" INTEGER,

    CONSTRAINT "legislation_version_tag_pkey" PRIMARY KEY ("legislation_version_tag_id")
);

-- CreateIndex
CREATE INDEX "ix_appropriations_appropriation_fiscal_years" ON "appropriations"."appropriation"("fiscal_years");

-- CreateIndex
CREATE INDEX "ix_appropriations_appropriation_legislation_content_id" ON "appropriations"."appropriation"("legislation_content_id");

-- CreateIndex
CREATE INDEX "ix_appropriations_appropriation_legislation_version_id" ON "appropriations"."appropriation"("legislation_version_id");

-- CreateIndex
CREATE INDEX "ix_appropriations_appropriation_prompt_batch_id" ON "appropriations"."appropriation"("prompt_batch_id");

-- CreateIndex
CREATE INDEX "ix_prompts_prompt_batch_legislation_version_id" ON "prompts"."prompt_batch"("legislation_version_id");

-- CreateIndex
CREATE INDEX "ix_prompts_prompt_batch_prompt_id" ON "prompts"."prompt_batch"("prompt_id");

-- CreateIndex
CREATE INDEX "ix_legislation_chamber" ON "legislation"("chamber");

-- CreateIndex
CREATE INDEX "ix_legislation_legislative_subjects" ON "legislation"("legislative_subjects");

-- CreateIndex
CREATE INDEX "ix_legislation_policy_areas" ON "legislation"("policy_areas");

-- CreateIndex
CREATE UNIQUE INDEX "unq_bill" ON "legislation"("chamber", "number", "legislation_type", "congress_id");

-- CreateIndex
CREATE INDEX "ix_legislation_action_parse_legislation_content_id" ON "legislation_action_parse"("legislation_content_id");

-- CreateIndex
CREATE INDEX "ix_legislation_action_parse_legislation_version_id" ON "legislation_action_parse"("legislation_version_id");

-- CreateIndex
CREATE INDEX "ix_legislation_committee_committee_id" ON "legislation_committee"("committee_id");

-- CreateIndex
CREATE INDEX "ix_legislation_committee_congress_id" ON "legislation_committee"("congress_id");

-- CreateIndex
CREATE INDEX "ix_legislation_committee_parent_id" ON "legislation_committee"("parent_id");

-- CreateIndex
CREATE INDEX "ix_legislation_committee_thomas_id" ON "legislation_committee"("thomas_id");

-- CreateIndex
CREATE INDEX "ix_legislation_committee_association_congress_id" ON "legislation_committee_association"("congress_id");

-- CreateIndex
CREATE INDEX "ix_legislation_committee_association_legislation_committee_id" ON "legislation_committee_association"("legislation_committee_id");

-- CreateIndex
CREATE INDEX "ix_legislation_committee_association_legislation_id" ON "legislation_committee_association"("legislation_id");

-- CreateIndex
CREATE INDEX "ix_legislation_content_legislation_version_id" ON "legislation_content"("legislation_version_id");

-- CreateIndex
CREATE INDEX "ix_legislation_content_summary_legislation_content_id" ON "legislation_content_summary"("legislation_content_id");

-- CreateIndex
CREATE INDEX "ix_legislation_content_summary_prompt_batch_id" ON "legislation_content_summary"("prompt_batch_id");

-- CreateIndex
CREATE INDEX "ix_legislation_content_tag_legislation_content_id" ON "legislation_content_tag"("legislation_content_id");

-- CreateIndex
CREATE INDEX "ix_legislation_content_tag_prompt_batch_id" ON "legislation_content_tag"("prompt_batch_id");

-- CreateIndex
CREATE INDEX "ix_legislation_content_tag_tags" ON "legislation_content_tag"("tags");

-- CreateIndex
CREATE INDEX "ix_legislation_sponsorship_cosponsor" ON "legislation_sponsorship"("cosponsor");

-- CreateIndex
CREATE INDEX "ix_legislation_sponsorship_legislation_id" ON "legislation_sponsorship"("legislation_id");

-- CreateIndex
CREATE INDEX "ix_legislation_sponsorship_legislator_bioguide_id" ON "legislation_sponsorship"("legislator_bioguide_id");

-- CreateIndex
CREATE INDEX "ix_legislation_sponsorship_original" ON "legislation_sponsorship"("original");

-- CreateIndex
CREATE INDEX "ix_legislation_sponsorship_sponsorship_withdrawn_date" ON "legislation_sponsorship"("sponsorship_withdrawn_date");

-- CreateIndex
CREATE INDEX "ix_legislation_version_legislation_id" ON "legislation_version"("legislation_id");

-- CreateIndex
CREATE INDEX "ix_legislation_version_legislation_version" ON "legislation_version"("legislation_version");

-- CreateIndex
CREATE INDEX "ix_legislation_version_version_id" ON "legislation_version"("version_id");

-- CreateIndex
CREATE INDEX "legis_version" ON "legislation_version"("legislation_version", "legislation_id");

-- CreateIndex
CREATE INDEX "ix_legislation_vote_congress_id" ON "legislation_vote"("congress_id");

-- CreateIndex
CREATE INDEX "ix_legislation_vote_id" ON "legislation_vote"("id");

-- CreateIndex
CREATE INDEX "ix_legislation_vote_legislation_id" ON "legislation_vote"("legislation_id");

-- CreateIndex
CREATE INDEX "ix_legislation_vote_number" ON "legislation_vote"("number");

-- CreateIndex
CREATE INDEX "ix_legislation_vote_question" ON "legislation_vote"("question");

-- CreateIndex
CREATE UNIQUE INDEX "ix_legislative_policy_area_name" ON "legislative_policy_area"("name");

-- CreateIndex
CREATE INDEX "ix_legislative_policy_area_congress_id" ON "legislative_policy_area"("congress_id");

-- CreateIndex
CREATE UNIQUE INDEX "unq_leg_pol" ON "legislative_policy_area"("name", "congress_id");

-- CreateIndex
CREATE INDEX "ix_legislative_policy_area_association_legislation_id" ON "legislative_policy_area_association"("legislation_id");

-- CreateIndex
CREATE INDEX "ix_legislative_policy_area_association_legislative_poli_2fd5" ON "legislative_policy_area_association"("legislative_policy_area_id");

-- CreateIndex
CREATE INDEX "ix_legislative_subject_congress_id" ON "legislative_subject"("congress_id");

-- CreateIndex
CREATE INDEX "ix_legislative_subject_subject" ON "legislative_subject"("subject");

-- CreateIndex
CREATE UNIQUE INDEX "unq_leg_subj" ON "legislative_subject"("subject", "congress_id");

-- CreateIndex
CREATE INDEX "ix_legislative_subject_association_legislation_id" ON "legislative_subject_association"("legislation_id");

-- CreateIndex
CREATE INDEX "ix_legislative_subject_association_legislative_subject_id" ON "legislative_subject_association"("legislative_subject_id");

-- CreateIndex
CREATE UNIQUE INDEX "ix_legislator_bioguide_id" ON "legislator"("bioguide_id");

-- CreateIndex
CREATE INDEX "ix_legislator_district" ON "legislator"("district");

-- CreateIndex
CREATE INDEX "ix_legislator_lis_id" ON "legislator"("lis_id");

-- CreateIndex
CREATE INDEX "ix_legislator_party" ON "legislator"("party");

-- CreateIndex
CREATE INDEX "ix_legislator_state" ON "legislator"("state");

-- CreateIndex
CREATE INDEX "ix_legislator_vote_id" ON "legislator_vote"("id");

-- CreateIndex
CREATE INDEX "ix_legislator_vote_legislation_vote_id" ON "legislator_vote"("legislation_vote_id");

-- CreateIndex
CREATE INDEX "ix_legislator_vote_legislator_bioguide_id" ON "legislator_vote"("legislator_bioguide_id");

-- CreateIndex
CREATE INDEX "ix_usc_act_section_usc_popular_name_id" ON "usc_act_section"("usc_popular_name_id");

-- CreateIndex
CREATE INDEX "ix_usc_chapter_version_id" ON "usc_chapter"("version_id");

-- CreateIndex
CREATE INDEX "content_ident" ON "usc_content"("usc_ident", "version_id");

-- CreateIndex
CREATE INDEX "ix_usc_content_parent_id" ON "usc_content"("parent_id");

-- CreateIndex
CREATE INDEX "ix_usc_content_usc_section_id" ON "usc_content"("usc_section_id");

-- CreateIndex
CREATE INDEX "ix_usc_content_version_id" ON "usc_content"("version_id");

-- CreateIndex
CREATE INDEX "ix_usc_content_diff_legislation_content_id" ON "usc_content_diff"("legislation_content_id");

-- CreateIndex
CREATE INDEX "ix_usc_content_diff_usc_chapter_id" ON "usc_content_diff"("usc_chapter_id");

-- CreateIndex
CREATE INDEX "ix_usc_content_diff_usc_content_id" ON "usc_content_diff"("usc_content_id");

-- CreateIndex
CREATE INDEX "ix_usc_content_diff_usc_section_id" ON "usc_content_diff"("usc_section_id");

-- CreateIndex
CREATE INDEX "ix_usc_content_diff_version_id" ON "usc_content_diff"("version_id");

-- CreateIndex
CREATE INDEX "ix_usc_popular_name_usc_release_id" ON "usc_popular_name"("usc_release_id");

-- CreateIndex
CREATE INDEX "ix_usc_section_parent_id" ON "usc_section"("parent_id");

-- CreateIndex
CREATE INDEX "ix_usc_section_usc_chapter_id" ON "usc_section"("usc_chapter_id");

-- CreateIndex
CREATE INDEX "ix_usc_section_version_id" ON "usc_section"("version_id");

-- CreateIndex
CREATE INDEX "ix_version_base_id" ON "version"("base_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_legislation_legislation_id" ON "sensitive"."user_legislation"("legislation_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_legislation_user_id" ON "sensitive"."user_legislation"("user_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_legislator_bioguide_id" ON "sensitive"."user_legislator"("bioguide_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_legislator_user_id" ON "sensitive"."user_legislator"("user_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_llm_query_legislation_version_id" ON "sensitive"."user_llm_query"("legislation_version_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_llm_query_query" ON "sensitive"."user_llm_query"("query");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_llm_query_user_id" ON "sensitive"."user_llm_query"("user_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_usc_content_user_id" ON "sensitive"."user_usc_content"("user_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_usc_content_user_usc_content_folder_id" ON "sensitive"."user_usc_content"("user_usc_content_folder_id");

-- CreateIndex
CREATE INDEX "ix_sensitive_user_usc_content_folder_user_id" ON "sensitive"."user_usc_content_folder"("user_id");

-- CreateIndex
CREATE INDEX "ix_legislation_action_legislation_id" ON "legislation_action"("legislation_id");

-- CreateIndex
CREATE INDEX "ix_legislation_version_tag_legislation_version_id" ON "legislation_version_tag"("legislation_version_id");

-- CreateIndex
CREATE INDEX "ix_legislation_version_tag_prompt_batch_id" ON "legislation_version_tag"("prompt_batch_id");

-- CreateIndex
CREATE INDEX "ix_legislation_version_tag_tags" ON "legislation_version_tag"("tags");

-- AddForeignKey
ALTER TABLE "appropriations"."appropriation" ADD CONSTRAINT "appropriation_legislation_content_id_fkey" FOREIGN KEY ("legislation_content_id") REFERENCES "legislation_content"("legislation_content_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "appropriations"."appropriation" ADD CONSTRAINT "appropriation_legislation_version_id_fkey" FOREIGN KEY ("legislation_version_id") REFERENCES "legislation_version"("legislation_version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "appropriations"."appropriation" ADD CONSTRAINT "appropriation_prompt_batch_id_fk" FOREIGN KEY ("prompt_batch_id") REFERENCES "prompts"."prompt_batch"("prompt_batch_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "prompts"."prompt_batch" ADD CONSTRAINT "prompt_batch_legislation_version_id_fkey" FOREIGN KEY ("legislation_version_id") REFERENCES "legislation_version"("legislation_version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "prompts"."prompt_batch" ADD CONSTRAINT "prompt_batch_prompt_id_fkey" FOREIGN KEY ("prompt_id") REFERENCES "prompts"."prompt"("prompt_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation" ADD CONSTRAINT "legislation_congress_id_fkey" FOREIGN KEY ("congress_id") REFERENCES "congress"("congress_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation" ADD CONSTRAINT "legislation_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "version"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_action_parse" ADD CONSTRAINT "legislation_action_parse_legislation_content_id_fkey" FOREIGN KEY ("legislation_content_id") REFERENCES "legislation_content"("legislation_content_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_action_parse" ADD CONSTRAINT "legislation_action_parse_legislation_version_id_fkey" FOREIGN KEY ("legislation_version_id") REFERENCES "legislation_version"("legislation_version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_committee" ADD CONSTRAINT "legislation_committee_congress_id_fkey" FOREIGN KEY ("congress_id") REFERENCES "congress"("congress_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_committee" ADD CONSTRAINT "legislation_committee_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "legislation_committee"("legislation_committee_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_committee_association" ADD CONSTRAINT "legislation_committee_association_congress_id_fkey" FOREIGN KEY ("congress_id") REFERENCES "congress"("congress_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_committee_association" ADD CONSTRAINT "legislation_committee_association_legislation_committee_id_fkey" FOREIGN KEY ("legislation_committee_id") REFERENCES "legislation_committee"("legislation_committee_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_committee_association" ADD CONSTRAINT "legislation_committee_association_legislation_id_fkey" FOREIGN KEY ("legislation_id") REFERENCES "legislation"("legislation_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_content" ADD CONSTRAINT "legislation_content_legislation_version_id_fkey" FOREIGN KEY ("legislation_version_id") REFERENCES "legislation_version"("legislation_version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_content" ADD CONSTRAINT "legislation_content_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "legislation_content"("legislation_content_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_content_summary" ADD CONSTRAINT "legislation_content_summary_legislation_content_id_fkey" FOREIGN KEY ("legislation_content_id") REFERENCES "legislation_content"("legislation_content_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_content_summary" ADD CONSTRAINT "legislation_content_summary_prompt_batch_id_fkey" FOREIGN KEY ("prompt_batch_id") REFERENCES "prompts"."prompt_batch"("prompt_batch_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_content_tag" ADD CONSTRAINT "legislation_content_tag_legislation_content_id_fkey" FOREIGN KEY ("legislation_content_id") REFERENCES "legislation_content"("legislation_content_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_content_tag" ADD CONSTRAINT "legislation_content_tag_prompt_batch_id_fkey" FOREIGN KEY ("prompt_batch_id") REFERENCES "prompts"."prompt_batch"("prompt_batch_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_sponsorship" ADD CONSTRAINT "legislation_sponsorship_legislation_id_fkey" FOREIGN KEY ("legislation_id") REFERENCES "legislation"("legislation_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_sponsorship" ADD CONSTRAINT "legislation_sponsorship_legislator_bioguide_id_fkey" FOREIGN KEY ("legislator_bioguide_id") REFERENCES "legislator"("bioguide_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_version" ADD CONSTRAINT "legislation_version_legislation_id_fkey" FOREIGN KEY ("legislation_id") REFERENCES "legislation"("legislation_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_version" ADD CONSTRAINT "legislation_version_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "version"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_vote" ADD CONSTRAINT "legislation_vote_congress_id_fkey" FOREIGN KEY ("congress_id") REFERENCES "congress"("congress_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_vote" ADD CONSTRAINT "legislation_vote_legislation_id_fkey" FOREIGN KEY ("legislation_id") REFERENCES "legislation"("legislation_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislative_policy_area" ADD CONSTRAINT "legislative_policy_area_congress_id_fkey" FOREIGN KEY ("congress_id") REFERENCES "congress"("congress_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislative_policy_area_association" ADD CONSTRAINT "legislative_policy_area_associa_legislative_policy_area_id_fkey" FOREIGN KEY ("legislative_policy_area_id") REFERENCES "legislative_policy_area"("legislative_policy_area_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislative_policy_area_association" ADD CONSTRAINT "legislative_policy_area_association_legislation_id_fkey" FOREIGN KEY ("legislation_id") REFERENCES "legislation"("legislation_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislative_subject" ADD CONSTRAINT "legislative_subject_congress_id_fkey" FOREIGN KEY ("congress_id") REFERENCES "congress"("congress_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislative_subject_association" ADD CONSTRAINT "legislative_subject_association_legislation_id_fkey" FOREIGN KEY ("legislation_id") REFERENCES "legislation"("legislation_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislative_subject_association" ADD CONSTRAINT "legislative_subject_association_legislative_subject_id_fkey" FOREIGN KEY ("legislative_subject_id") REFERENCES "legislative_subject"("legislative_subject_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislator_vote" ADD CONSTRAINT "legislator_vote_legislation_vote_id_fkey" FOREIGN KEY ("legislation_vote_id") REFERENCES "legislation_vote"("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislator_vote" ADD CONSTRAINT "legislator_vote_legislator_bioguide_id_fkey" FOREIGN KEY ("legislator_bioguide_id") REFERENCES "legislator"("bioguide_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_act_section" ADD CONSTRAINT "usc_act_section_usc_popular_name_id_fkey" FOREIGN KEY ("usc_popular_name_id") REFERENCES "usc_popular_name"("usc_popular_name_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_chapter" ADD CONSTRAINT "usc_chapter_usc_release_id_fkey" FOREIGN KEY ("usc_release_id") REFERENCES "usc_release"("usc_release_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_chapter" ADD CONSTRAINT "usc_chapter_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "version"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_content" ADD CONSTRAINT "usc_content_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "usc_content"("usc_content_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_content" ADD CONSTRAINT "usc_content_usc_section_id_fkey" FOREIGN KEY ("usc_section_id") REFERENCES "usc_section"("usc_section_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_content" ADD CONSTRAINT "usc_content_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "version"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_content_diff" ADD CONSTRAINT "usc_content_diff_legislation_content_id_fkey" FOREIGN KEY ("legislation_content_id") REFERENCES "legislation_content"("legislation_content_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_content_diff" ADD CONSTRAINT "usc_content_diff_usc_chapter_id_fkey" FOREIGN KEY ("usc_chapter_id") REFERENCES "usc_chapter"("usc_chapter_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_content_diff" ADD CONSTRAINT "usc_content_diff_usc_content_id_fkey" FOREIGN KEY ("usc_content_id") REFERENCES "usc_content"("usc_content_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_content_diff" ADD CONSTRAINT "usc_content_diff_usc_section_id_fkey" FOREIGN KEY ("usc_section_id") REFERENCES "usc_section"("usc_section_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_content_diff" ADD CONSTRAINT "usc_content_diff_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "version"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_popular_name" ADD CONSTRAINT "usc_popular_name_usc_release_id_fkey" FOREIGN KEY ("usc_release_id") REFERENCES "usc_release"("usc_release_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_release" ADD CONSTRAINT "usc_release_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "version"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_section" ADD CONSTRAINT "usc_section_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "usc_section"("usc_section_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_section" ADD CONSTRAINT "usc_section_usc_chapter_id_fkey" FOREIGN KEY ("usc_chapter_id") REFERENCES "usc_chapter"("usc_chapter_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usc_section" ADD CONSTRAINT "usc_section_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "version"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "version" ADD CONSTRAINT "version_base_id_fkey" FOREIGN KEY ("base_id") REFERENCES "version"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_legislation" ADD CONSTRAINT "user_legislation_legislation_id_fkey" FOREIGN KEY ("legislation_id") REFERENCES "legislation"("legislation_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_legislation" ADD CONSTRAINT "user_legislation_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "sensitive"."user_ident"("user_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_legislator" ADD CONSTRAINT "user_legislator_bioguide_id_fkey" FOREIGN KEY ("bioguide_id") REFERENCES "legislator"("bioguide_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_legislator" ADD CONSTRAINT "user_legislator_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "sensitive"."user_ident"("user_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_llm_query" ADD CONSTRAINT "user_llm_query_legislation_version_id_fkey" FOREIGN KEY ("legislation_version_id") REFERENCES "legislation_version"("legislation_version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_llm_query" ADD CONSTRAINT "user_llm_query_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "sensitive"."user_ident"("user_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_usc_content" ADD CONSTRAINT "user_usc_content_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "sensitive"."user_ident"("user_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_usc_content" ADD CONSTRAINT "user_usc_content_user_usc_content_folder_id_fkey" FOREIGN KEY ("user_usc_content_folder_id") REFERENCES "sensitive"."user_usc_content_folder"("user_usc_content_folder_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sensitive"."user_usc_content_folder" ADD CONSTRAINT "user_usc_content_folder_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "sensitive"."user_ident"("user_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_action" ADD CONSTRAINT "legislation_action_legislation_id_fkey" FOREIGN KEY ("legislation_id") REFERENCES "legislation"("legislation_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_version_tag" ADD CONSTRAINT "legislation_version_tag_legislation_version_id_fkey" FOREIGN KEY ("legislation_version_id") REFERENCES "legislation_version"("legislation_version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "legislation_version_tag" ADD CONSTRAINT "legislation_version_tag_prompt_batch_id_fkey" FOREIGN KEY ("prompt_batch_id") REFERENCES "prompts"."prompt_batch"("prompt_batch_id") ON DELETE CASCADE ON UPDATE NO ACTION;

