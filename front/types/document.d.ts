export type Block = {
	title: string;
	summary: string;
};

export type Document = {
	id: string;
	title: string;
	summary: string;
	keywords?: string;
	tags?: []string;
	recommendations?: []string;
	blocks: []Block;
};
