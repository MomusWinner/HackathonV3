export type Block = {
	title: string;
	summary: string;
};

export type DocumentStatus = "completed" | "processing";

export type DocumentBrief = {
	id: string;
	title: string;
	processing_status: DocumentStatus;
};

export type Document = {
	id: string;
	processing_status: DocumentStatus;
	title: string;
	summary: string;
	keywords?: string;
	tags?: string[];
	recommendations?: string[];
	blocks: Block[];
};
