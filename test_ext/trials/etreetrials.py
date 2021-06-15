from lxml import etree

root = etree.XML("<root><a x='123'>aText<b/><c/><b/></a></root>")
print(root.find(".//B").tag)
