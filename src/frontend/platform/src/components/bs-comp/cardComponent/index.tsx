import { AssistantIcon, FlowIcon } from "@/components/bs-icons/";
import { cname } from "@/components/bs-ui/utils";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { SkillIcon } from "../../bs-icons";
import { AddToIcon } from "../../bs-icons/addTo";
import { DelIcon } from "../../bs-icons/del";
import { GoIcon } from "../../bs-icons/go";
import { PlusIcon } from "../../bs-icons/plus";
import { SettingIcon } from "../../bs-icons/setting";
import { UserIcon } from "../../bs-icons/user";
import { UpvoteIcon, UpvotedIcon, HotIcon } from "../../bs-icons/upvote"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../../bs-ui/card";
import { Switch } from "../../bs-ui/switch";
import { captureAndAlertRequestErrorHoc } from "@/controllers/request";
import { getUpvoteApi, createUpvoteApi, updateUpvoteApi } from "@/controllers/API/upvite";
import { useToast } from "@/components/bs-ui/toast/use-toast";

interface IProps<T> {
  data: T,
  /** id为''时，表示新建 */
  id?: number | string,
  logo?: string,
  type: "skill" | "sheet" | "assistant" | "setting", // 技能列表｜侧边弹窗列表
  title: string,
  edit?: boolean,
  description: React.ReactNode | string,
  checked?: boolean,
  lighten?: boolean,
  counts?: number,
  ms_counts?: number,
  user?: string,
  currentUser?: any,
  labelPannel?: React.ReactNode,
  isAdmin?: boolean,
  headSelecter?: React.ReactNode,
  footer?: React.ReactNode,
  icon?: any,
  onClick?: () => void,
  onSwitchClick?: () => void,
  onAddTemp?: (data: T) => void,
  onCheckedChange?: (b: boolean, data: T) => Promise<any>
  onDelete?: (data: T) => void,
  onSetting?: (data: T) => void,
}

export const gradients = [
  'bg-amber-500',
  'bg-orange-600',
  'bg-teal-500',
  'bg-purple-600',
  'bg-blue-700'
]

// 'bg-slate-600',
// 'bg-amber-500',
// 'bg-red-600',
// 'bg-orange-600',
// 'bg-teal-500',
// 'bg-purple-600',
// 'bg-blue-700',
// 'bg-yellow-600',
// 'bg-emerald-600',
// 'bg-green-700',
// 'bg-cyan-600',
// 'bg-sky-600',
// 'bg-indigo-600',
// 'bg-violet-600',
// 'bg-purple-600',
// 'bg-fuchsia-700',
// 'bg-pink-600',
// 'bg-rose-600'
export function TitleIconBg({ id, className = '', children = <SkillIcon /> }) {
  return <div className={cname(`rounded-md flex justify-center items-center ${gradients[parseInt(id + '', 16) % gradients.length]}`, className)}>{children}</div>
}

export function TitleLogo({ id = 0, url, className = '', children = <SkillIcon /> }) {
  return url ? <img src={url} className={cname(`w-10 h-10 rounded-sm object-cover`, className)} /> : <TitleIconBg id={id} className={className}>{children}</TitleIconBg>
}

export function TitleLogoSide({ id = 0, url, className = '', children = <SkillIcon /> }) {
  return url ? <img src={url} className={cname(`w-6 h-6 rounded-sm object-cover`, className)} /> : <TitleIconBg id={id} className={className}>{children}</TitleIconBg>
}

export default function CardComponent<T>({
  id = '',
  logo = '',
  data,
  type,
  icon: Icon = SkillIcon,
  edit = false,
  user,
  labelPannel = null,
  title,
  checked,
  lighten,
  counts,
  ms_counts,
  isAdmin,
  description,
  footer = null,
  headSelecter = null,
  onClick,
  onSwitchClick,
  onDelete,
  onAddTemp,
  onCheckedChange,
  onSetting
}: IProps<T>) {

  const [_checked, setChecked] = useState(checked)
  const [islighten, setLighten] = useState(lighten)
  const [count, setCount] = useState(counts)
  const [ms_count, setMsCount] = useState(ms_counts)

  const { t } = useTranslation()

  const { message } = useToast();

  const handleCheckedChange = async (bln) => {
    const res = await onCheckedChange(bln, data)
    if (res === false) return
    setChecked(bln)
  }

  const upvote = async (id,  type) => {
    const newState = !islighten
    console.log('newState', newState)
    setLighten(newState)
    const status = newState ? 1: 2
    let messageText = newState ? '收藏成功': '已取消收藏'
    // 先执行更新操作
    const updateRes = await captureAndAlertRequestErrorHoc(
        updateUpvoteApi(id, type, status)
    );
    console.log('updateRes', updateRes)
    if (updateRes === false) return;
    // 更新成功后，获取最新的点赞数
    const countRes = await captureAndAlertRequestErrorHoc(
        getUpvoteApi(id, type)
    );
    if (countRes === false) return;
    console.log('countRes', countRes)
    setCount(countRes);
    message({description: messageText, variant: "success"});
  }

  const hot = async (id, type) => {
    let messageText = '使用可以增加热度'
    message({description: messageText, variant: "success"});
  }

  const userName = localStorage.getItem("user_name") || '';

  // 新建小卡片（sheet）
  if (!id && type === 'sheet') return <Card className="group w-[320px] cursor-pointer border-dashed border-[#BEC6D6] transition hover:border-primary hover:shadow-none bg-background-new" onClick={onClick}>
    <CardHeader>
      <CardTitle>
        <div className="flex gap-2 items-center">
          <div className="justify-between"><PlusIcon className="group-hover:text-primary transition-none" /></div>
          <span>{title}</span>
        </div>
      </CardTitle>
    </CardHeader>
    <CardContent className="h-fit max-h-[44px] overflow-auto scrollbar-hide">
      <CardDescription className="break-all">{description}</CardDescription>
    </CardContent>
    <CardFooter className="flex justify-end h-10">
      <div className="rounded cursor-pointer"><GoIcon className="group-hover:text-primary transition-none"/></div>
    </CardFooter>
  </Card>


  // 新建卡片
  if (!id) return <Card className="group w-[320px] cursor-pointer border-dashed border-[#BEC6D6] transition hover:border-primary hover:shadow-none bg-background-new" onClick={onClick}>
    <CardHeader>
      <div className="flex justify-between pb-2"><PlusIcon className="group-hover:text-primary transition-none" /></div>
      <CardTitle className="">{title}</CardTitle>
    </CardHeader>
    <CardContent className="h-[140px] overflow-auto scrollbar-hide">
      <CardDescription>{description}</CardDescription>
    </CardContent>
    <CardFooter className="flex justify-end h-10">
      <div className="rounded cursor-pointer"><GoIcon className="group-hover:text-primary transition-none dark:text-slate-50" /></div>
    </CardFooter>
  </Card>

  // 热门推荐列表
  if (type === 'hotsheet') return <Card className="group max-h-[156px] w-[346px] cursor-pointer bg-[#F7F9FC] dark:bg-background-main dark:hover:bg-background-login hover:bg-[#EDEFF6] hover:shadow-none relative" onClick={onClick}>
    <CardHeader className="pb-2">
      <CardTitle className="truncate-doubleline">
        <div className="flex gap-2 pb-2 items-center">
          <TitleLogoSide
              url={logo}
              id={id}
          >
            <Icon />
          </TitleLogoSide>
          <p className="leading-5 align-middle">{title}</p>
          <div className="flex gap-2 ml-auto flex-wrap">
            {data.tags.length > 0 && data.tags.map(({ id, name }) => (
                <span key={id} className="space-x-2 mb-2">
                  <label className="text-sm rounded text-primary">{name}</label>
                </span>
            ))}
            {data.version_list.length > 0 && data.version_list.filter( v => v.is_current === 1).map(({ id, name }) => (
                <span key={id} className="space-x-2 mb-2">
                  <label className="text-sm rounded text-primary">{name}</label>
                </span>
            ))}
          </div>
        </div>
        {/* <span></span> */}
      </CardTitle>
    </CardHeader>
    <CardContent className="h-[60px] overflow-auto scrollbar-hide mb-2">
      <CardDescription className="break-all">{description}</CardDescription>
    </CardContent>
    { /* 收藏和热度 */}
    <div className="flex gap-2 p-5 pb-4 pt-0">
      {islighten ? <div className="w-1/4 flex items-center gap-1 text-sm hover:bg-[#EAEDF3] rounded cursor-pointer"
                        onClick={(e) => {
                          e.stopPropagation();
                          upvote(data.id, data.flow_type);
                        }}>
            <UpvotedIcon/>{count}</div>
          : <div className="w-1/4 flex items-center gap-1 text-sm hover:bg-[#EAEDF3] rounded cursor-pointer"
                 onClick={(e) => {
                   e.stopPropagation();
                   upvote(data.id, data.flow_type);
                 }}>
            <UpvoteIcon className="mr-1"/>{count}</div>}
      <div className="w-1/4 flex items-center gap-1 text-sm hover:bg-[#EAEDF3] rounded cursor-pointer"
           onClick={(e) => {
             e.stopPropagation();
             hot(data.id, data.flow_type);
           }}>
        <HotIcon/>{ms_count}</div>
    </div>
    <CardFooter className=" block">
      {footer}
    </CardFooter>
  </Card>

  // 侧边弹窗列表（sheet）
  if (type === 'sheet') return <Card className="group max-h-[146px] w-[316px] cursor-pointer bg-[#F7F9FC] dark:bg-background-main dark:hover:bg-background-login hover:bg-[#EDEFF6] hover:shadow-none relative" onClick={onClick}>
    <CardHeader className="pb-2">
      <CardTitle className="truncate-doubleline">
        <div className="flex gap-2 pb-2 items-center">
          <TitleLogoSide
            url={logo}
            id={id}
          >
            <Icon />
          </TitleLogoSide>
          <p className="leading-5 align-middle">{title}</p>
        </div>
        {/* <span></span> */}
      </CardTitle>
    </CardHeader>
    <CardContent className="h-[60px] overflow-auto scrollbar-hide mb-2">
      <CardDescription className="break-all">{description}</CardDescription>
    </CardContent>
    <CardFooter className=" block">
      {footer}
    </CardFooter>
  </Card>

// 助手&技能&工作流列表卡片组件
  return <Card className="group w-[320px] hover:bg-card/80 cursor-pointer grid" onClick={() => edit && onClick()}>
    <CardHeader>
      <div className="flex justify-between pb-2">
        <TitleLogo
          url={logo}
          id={id}
        >
          {type === 'skill' ? <SkillIcon /> : type === 'assistant' ? <AssistantIcon /> : <FlowIcon />}
        </TitleLogo>
        <div className="flex gap-1 items-center">
          {headSelecter}
          {(isAdmin || user === userName) && <Switch
            checked={_checked}
            className="w-12"
            // @ts-ignore
            texts={[t('skills.online'), t('skills.offline')]}
            onCheckedChange={(b) => edit && handleCheckedChange(b)}
            onClick={e => { e.stopPropagation(); onSwitchClick?.() }}
          ></Switch>}
        </div>
      </div>
      <CardTitle className="truncate-doubleline leading-5">{title}</CardTitle>
    </CardHeader>
    <CardContent className="h-[140px] overflow-auto scrollbar-hide">
      <CardDescription className="break-all">{description}</CardDescription>
    </CardContent>
    <CardFooter className="h-20 grid grid-rows-2 self-end">
      {labelPannel}
      <div className="flex justify-between items-center h-10">
        <div className="flex gap-1 items-center">
          <UserIcon />
          <span className="text-sm text-muted-foreground">{t('skills.createdBy')}</span>
          <span className="text-sm font-medium leading-none overflow-hidden text-ellipsis max-w-32 ">{user}</span>
        </div>
        {edit
          && <div className="hidden group-hover:flex">
            {!checked && <div className="hover:bg-[#EAEDF3] rounded cursor-pointer" onClick={(e) => { e.stopPropagation(); onSetting(data) }}><SettingIcon /></div>}
            {isAdmin && type !== 'assistant' && <div className="hover:bg-[#EAEDF3] rounded cursor-pointer" onClick={(e) => { e.stopPropagation(); onAddTemp(data) }}><AddToIcon /></div>}
            {!checked && <div className="hover:bg-[#EAEDF3] rounded cursor-pointer" onClick={(e) => { e.stopPropagation(); onDelete(data) }}><DelIcon /></div>}
          </div>
        }
      </div>
      {footer}
    </CardFooter>
  </Card>
};
