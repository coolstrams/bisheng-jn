import { Accordion } from "@/components/bs-ui/accordion";
import { Button } from "@/components/bs-ui/button";
import { SearchInput } from "@/components/bs-ui/input";
import { getAssistantToolsApi } from "@/controllers/API/assistant";
import { PersonIcon, StarFilledIcon } from "@radix-ui/react-icons";
import { useContext, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import EditTool from "./components/EditTool";
import ToolItem from "./components/ToolItem";
import ToolSet from "./components/ToolSet";
import { userContext } from "@/contexts/userContext";

export default function tabTools({ select = null, onSelect }) {
  const [keyword, setKeyword] = useState(" ");
  const [allData, setAllData] = useState([]);
  const { t } = useTranslation()

  const { user } = useContext(userContext)

  const [type, setType] = useState(""); // '' add edit
  const editRef = useRef(null);

  const loadData = (_type = "custom") => {
    getAssistantToolsApi(_type).then((res) => {
      setAllData(res);
      setKeyword("");
    });
  };
  useEffect(() => {
    loadData(type === "" ? "default" : "custom");
  }, [type]);

  const options = useMemo(() => {
    return allData.filter((el) => {
      // 搜索范围：工具名称、工具描述、工具api名称、工具api描述
      const targetStr = `${el.name}-${el.description}-${el.children?.map((el) => el.name + el.desc).join("-") || ''}`
      return targetStr.toLowerCase().includes(keyword.toLowerCase());
    });
  }, [keyword, allData]);

  const hasSet = (name) => {
    if (user.role !== 'admin') return false
    return ['Dalle3绘画', 'Bing web搜索', '天眼查'].includes(name)
  }

  const toolsetRef = useRef(null)

  return (
    <div className="flex h-full relative" onClick={(e) => e.stopPropagation()}>
      <div className="w-full flex h-full overflow-y-scroll scrollbar-hide relative bg-background-main border-t">
        <div className="w-fit p-6">
          {/* <h1>{t("tools.addTool")}</h1> */}
          <SearchInput
            placeholder={t("tools.search")}
            className="mt-6"
            onChange={(e) => setKeyword(e.target.value)}
          />
          <Button
            className="mt-4 w-full text-[white]"
            onClick={() => editRef.current.open()}
          >
            {t('create')}{t("tools.createCustomTool")}
          </Button>
          <div className="mt-4">
            <div
              className={`flex cursor-pointer items-center gap-2 rounded-md px-4 py-2 transition-all duration-200 hover:bg-muted-foreground/10 ${type === "" && "bg-muted-foreground/10"
                }`}
              onClick={() => setType("")}
            >
              <PersonIcon />
              <span>{t("tools.builtinTools")}</span>
            </div>
            <div
              className={`mt-1 flex cursor-pointer items-center gap-2 rounded-md px-4 py-2 transition-all duration-200 hover:bg-muted-foreground/10 ${type === "edit" && "bg-muted-foreground/10"
                }`}
              onClick={() => setType("edit")}
            >
              <StarFilledIcon />
              <span>{t("tools.customTools")}</span>
            </div>
          </div>
        </div>
        <div className="h-full w-full flex-1 overflow-auto bg-background-login p-5 pt-12 scrollbar-hide">
          <Accordion type="single" collapsible className="w-full">
            {options.length ? (
              options.map((el) => (
                <ToolItem
                  key={el.id}
                  type={type}
                  select={select}
                  data={el}
                  onSelect={onSelect}
                  onSetClick={hasSet(el.name) ? () => toolsetRef.current.edit(el) : null}
                  onEdit={(id) => editRef.current.edit(el)}
                ></ToolItem>
              ))
            ) : (
              <div className="mt-2 pt-40 text-center text-sm text-muted-foreground">
                {t("tools.empty")}
              </div>
            )}
          </Accordion>
        </div>
      </div>
      {/* footer */}
      <div className="absolute bottom-0 left-0 flex h-16 w-full items-center justify-between bg-background-login px-10">
        <p className="break-keep text-sm text-muted-foreground">
          {t("tools.manageCustomTools")}
        </p>
      </div>

      <EditTool
        onReload={() => {
          // 切换自定义工具 并 刷新
          setType('edit');
          type === 'edit' && loadData();
        }}
        ref={editRef}
      />
      <ToolSet ref={toolsetRef} onChange={() => loadData("default")} />
    </div>
  );
}