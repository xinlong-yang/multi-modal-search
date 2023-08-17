# multi-modal-search
这是一个爬虫文件，可以爬取CVPR, ACL, ICML, NIPS以及ICLR上面指定学校和内容的文章。您可以在self.top20中指定你需要的学校，然后在self.prompts中输入你需要读的paper的主要关键词（包含在摘要中）。当前默认是爬取2022年有关多模态主题的文章，筛选的是北美top20的学校的文章，筛选规则默认是一作或者通讯在self.top20中。
